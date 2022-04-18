import re

from playwright.sync_api import Playwright, sync_playwright, expect
from packages.configreader import config_reader
from time import strftime, localtime
from loguru import logger
from json import dumps as jsondumps

PROXY_HTTP = "http://127.0.0.1:54433"
# PROXY_SOCKS5 = "socks5://127.0.0.1:51837"

browserLaunchOptionDict = {
    "headless": True,
    "proxy": {
        "server": PROXY_HTTP,
    }
}


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


def sid_response(response):
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


def run(playwright: Playwright) -> None:
    logger.info("读取配置文件")
    config = config_reader("osu_account")
    logger.info("playwright: 打开浏览器")
    browser = playwright.chromium.launch(**browserLaunchOptionDict)
    context = browser.new_context()

    context.route("**/*.{png,jpg,jpeg}", lambda route: route.abort())
    context.route(re.compile(r"(\.png$)|(\.jpg$)|(\.jpeg$)"), lambda route: route.abort())

    page = browser.new_page()

    logger.info("playwright: 跳转至osu.ppy.sh/beatmapsets")
    page.goto("https://osu.ppy.sh/beatmapsets", timeout=3000000)

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
        # 滚动到页面底部
        page.wait_for_timeout(500)  # 等待五秒滚动一次
        page.evaluate("window.scrollTo(0,document.body.scrollHeight);")

    # ---------------------
    context.close()
    browser.close()

