from datetime import datetime

import httpx
import pymongo
import retrying

from .configreader import config_reader
from loguru import logger

CONFIG = config_reader("get_map")


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
                i: dict
                data = {}
                for key, value in i.items():
                    # 如果第一层里边有时间，转换为datetime
                    if key in ["last_updated", "ranked_date", "submitted_date"]:
                        try:  # try的原因是有的不会必然是时间，比如ranked_date
                            n_value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S+00:00')
                            data[key] = n_value
                            continue
                        except Exception:  # 这种情况下就直接塞进去
                            data[key] = value
                            continue

                    # 遍历第二层，也就是单个beatmap，查询时间
                    if key == "beatmaps":
                        datab = {}
                        for keyb, valueb in value:
                            if keyb == "last_updated":
                                try:
                                    n_valueb = datetime.strptime(valueb, '%Y-%m-%dT%H:%M:%S+00:00')
                                    datab[keyb] = n_valueb
                                    continue
                                except Exception:
                                    datab[keyb] = valueb
                                    continue
                            datab[keyb] = valueb
                        data[key] = datab
                    data[key] = value

                MONGO.update_one({"id": data["id"]}, {"$set": data}, upsert=True)
                n += 1
            logger.info(f"保存或更新{n}数据到mongodb")
            return n
        except Exception as e:
            logger.error(e)
    except Exception:
        pass


@retrying.retry
def update_new():
    # 判断代理
    if CONFIG["proxy"]["server"] not in [None, '']:
        proxies = {
            'http://': CONFIG["proxy"]["server"]
        }
    else:
        proxies = None
    params = {
        "s": "any"
    }
    url = "https://osu.ppy.sh/beatmapsets/search"

    with httpx.Client(proxies=proxies) as client:
        resp = client.get(url=url, params=params).json()
        save_to_mongodb(resp)


MONGO = connect_to_mongodb()
