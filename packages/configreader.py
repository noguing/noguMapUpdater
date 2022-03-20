import json


def config_reader(content_to_return: str) -> dict:
    j = json.load(open("config.json", 'r'))
    match content_to_return:
        case "osu_client": return j["osu_client"]
        case "mysql": return j["mysql"]
