import re
import pymongo

from playwright.sync_api import Playwright
from packages.configreader import config_reader
from time import strftime, localtime
from loguru import logger
from json import dumps as jsondumps


CONFIG = config_reader("get_map")


# 生成器，负责分文件进行保存
def file_reset():
    fp = f"data/{strftime('%Y-%m-%d-%H-%M-%S', localtime())}.json"
    with open(fp, "a") as now_file:  # 当前要写入的文件，以当前时间戳为文件名
        now_file.write("{\"request_list\":[")  # json文件前缀，为多次追加文本做铺垫
        logger.info(f"playwright: 当前文件: {fp}")

        file_input_count = 0  # 该文件现在写入了n次
        logger.info(f"playwright: 当前写入次数: {file_input_count}")
    yield fp, file_input_count
    while True:
        if file_input_count < 10:
            with open(fp, "a") as now_file:
                file_input_count += 1
                now_file.write(",")  # 写入","分割列表里每次保存的内容
                logger.info("playwright: 成功写入")
                logger.info(f"playwright: 当前写入次数: {file_input_count}")
        else:
            with open(fp, "a") as now_file:
                now_file.write("]}")  # 写入文件尾，使其形成正常的json文件
                now_file.close()
                logger.info("playwright: 防止内容过长，关闭原文件，创建新文件")

            fp = f"data/{strftime('%Y-%m-%d-%H-%M-%S', localtime())}.json"
            with open(fp, "a") as now_file:
                logger.info(f"playwright: 当前文件: {fp}")
                now_file.write("{\"request_list\":[")
                file_input_count = 0
                logger.info(f"playwright: 重置当前写入次数: {file_input_count}")
        yield fp, file_input_count


FR = file_reset()  # 初始化生成器


def save_to_file(response):
    try:  # 报错则不是json，不添加(铺面搜索界面的json只有铺面)
        resj = response.json()  # 放在前边，用于检测是否为json，不是直接报错退出等待下一次调用
        try:
            now_file, file_input_count = next(FR)
            with open(now_file, "a") as f:
                f.write(jsondumps(resj["beatmapsets"]))
        except Exception as e:
            logger.error(e)
        logger.info("playwright: 将铺面信息写入文件")
    except Exception as e:
        pass


def connect_to_mongodb():
    try:
        logger.info("尝试登入mongodb")
        mongo_config = config_reader("mongodb")
        if (mongo_config["user"] is None and mongo_config["password"] is None) or \
           (mongo_config["user"] == "" and mongo_config["password"] == ""):
            # 无密码连接
            logger.info("config.json中没有填写用户名与密码，采用无密码连接")
            mongo_client = pymongo.MongoClient(
                f"mongodb://{mongo_config['host']}:{mongo_config['port']}/")
        else:
            logger.info("在config.json中检测到用户名与密码，采用无密码连接")
            # 有密码连接
            mongo_client = pymongo.MongoClient(
                f"mongodb://{mongo_config['user']}:{mongo_config['password']}@{mongo_config['host']}:{mongo_config['port']}/")

        logger.info(f"链接信息:\n{mongo_client.server_info()}")

        logger.info(f"接入数据库{mongo_config['database']}")
        mongo_db = mongo_client[mongo_config["database"]]
        logger.info(f"接入表{mongo_config['collection']}")
        mongo_collection = mongo_db[mongo_config["collection"]]
    except Exception as e:
        logger.error(f"接入失败\n{e}")
        exit(0)
    return mongo_collection


if CONFIG["beatmapset_save_type"] == "mongodb":
    MONGO = connect_to_mongodb()


def save_to_mongodb(response):
    try:
        resj = response.json()
        try:
            logger.info("保存数据到mongodb")
            MONGO.insert_many([i for i in resj["beatmapsets"]])
        except Exception as e:
            logger.error(e)
    except Exception:
        pass


def sid_response(response):
    match CONFIG["beatmapset_save_type"]:
        case "file": save_to_file(response)
        case "mongodb": save_to_mongodb(response)


def run(playwright: Playwright) -> None:
    browser_launch_option_dict = {
        "headless": False
    }

    logger.info("读取配置文件")
    if CONFIG["proxy"]["server"] is None or CONFIG["proxy"]["server"] == "":
        browser_launch_option_dict["proxy"] = {
            "server": CONFIG["proxy"]["server"],
        }
    config = config_reader("osu_account")

    logger.info("playwright: 打开浏览器")
    browser = playwright.chromium.launch(**browser_launch_option_dict)
    context = browser.new_context()

    context.route("**/*.{png,jpg,jpeg}", lambda route: route.abort())
    context.route(re.compile(r"(\.png$)|(\.jpg$)|(\.jpeg$)"), lambda route: route.abort())

    page = browser.new_page()

    logger.info("playwright: 跳转至osu.ppy.sh/beatmapsets")
    page.goto("https://osu.ppy.sh/beatmapsets", timeout=3000000)

    # # 关闭图片加载
    # page.evaluate("document.querySelector(\".beatmapset-panel\").innerHTML = \"<span>F</span>\"")

    # Click .avatar.avatar--nav2
    page.locator(".avatar.avatar--nav2").click()

    logger.info("playwright: 输入用户名")
    # # Click [placeholder="用户名"]
    # page.locator("[placeholder=\"用户名\"]").click()

    # Fill [placeholder="用户名"]
    page.fill("body > div.login-box > div > form > div.login-box__row.login-box__row--inputs > "
              "input.login-box__form-input.js-login-form-input.js-nav2--autofocus", config["username"])

    logger.info("playwright: 输入密码")
    # # Click [placeholder="密码"]
    # page.locator("[placeholder=\"密码\"]").click()

    # Fill [placeholder="密码"]
    page.fill("body > div.login-box > div > form > div.login-box__row.login-box__row--inputs > input:nth-child(2)",
              config["password"])

    logger.info("playwright: 点击登录")
    # Click text=登录以继续 我忘记了我的登录信息 登录 >> button
    page.locator("body > div.login-box > div > form > div.login-box__row.login-box__row--actions > div > button")\
        .click()

    logger.info("playwright: 等待5秒开始遍历")
    # 等待十秒登录(
    page.wait_for_timeout(5000)

    logger.info("playwright: 切换为全部图而不是仅含有排行榜")
    # Click text=更多搜索选项
    page.locator("body > div.osu-layout__section.osu-layout__section--full.js-content.beatmaps_index > div > "
                 "div:nth-child(2) > div > div > a").click()

    # Click .beatmapsets-search div:nth-child(5) .beatmapsets-search-filter__items a >> nth=0
    page.locator("body > div.osu-layout__section.osu-layout__section--full.js-content.beatmaps_index > div > "
                 "div:nth-child(2) > div > div > div:nth-child(5) > div > a:nth-child(1)").click()

    logger.info("playwright: 开始监听类型response类型")
    # 监听response类型
    page.on("response", sid_response)

    logger.info("playwright: 开始遍历...")
    while True:
        # 滚动到页面顶部再回到底部
        page.wait_for_timeout(500)  # 等待五秒滚动一次
        page.evaluate("window.scrollTo(0,0);")
        page.evaluate("window.scrollTo(0,document.body.scrollHeight);")

    # ---------------------
    # context.close()
    # browser.close()

