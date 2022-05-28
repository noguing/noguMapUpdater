import pymongo

from packages.configreader import config_reader
from loguru import logger
from json import dumps as jsondumps
from time import strftime, localtime
import retrying
import httpx


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


def save_to_file(response):
    try:  # 报错则不是json，不添加(铺面搜索界面的json只有铺面)
        resj = response.json()  # 放在前边，用于检测是否为json，不是直接报错退出等待下一次调用
        try:
            now_file, file_input_count = next(FR)
            with open(now_file, "a") as f:
                f.write(jsondumps(resj["beatmapsets"]))
        except Exception as e:
            logger.error(e)
        logger.info("将铺面信息写入文件")
        return len(resj["beatmapsets"])
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
        return mongo_collection
    except Exception as e:
        logger.error(f"接入失败\n{e}")
        exit(0)


def save_to_mongodb(response):
    try:
        # resj = response.json()
        resj = response
        try:
            n = 0
            for i in resj["beatmapsets"]:
                MONGO.update_one({"id": i["id"]}, {"$set": i}, upsert=True)
                n += 1
            # logger.info(f"保存{n}数据到mongodb")
            return n
        except Exception as e:
            logger.error(e)
    except Exception:
        pass


def sid_response(response):
    match CONFIG["beatmapset_save_type"]:
        case "file":
            return save_to_file(response)
        case "mongodb":
            return save_to_mongodb(response)


CONFIG = config_reader("get_map")
match CONFIG["beatmapset_save_type"]:
    case "mongodb":
        MONGO = connect_to_mongodb()
    case "file":
        FR = file_reset()  # 初始化生成器


def run_map_get():
    # 判断代理
    if CONFIG["proxy"]["server"] not in [None, '']:
        proxies = {
            'http://': CONFIG["proxy"]["server"]
        }
    else:
        proxies = None

    with httpx.Client(proxies=proxies, timeout=60, verify=False) as client:
        params = {
            "s": "any"
        }
        url = "https://osu.ppy.sh/beatmapsets/search"
        have_saved = 0  # 初始化计数器
        while True:
            resp = client.get(url=url, params=params).json()
            if resp["total"] == 0:
                logger.error("没搜到...Not Found...")
                break

            @retrying.retry
            def save(resp):
                return sid_response(resp)
            have_saved += save(resp)
            logger.info(f"已经保存了{have_saved}条数据")
            params["cursor_string"] = resp["cursor_string"]
            if resp["cursor_string"] is None:
                logger.success("Done")
                break

