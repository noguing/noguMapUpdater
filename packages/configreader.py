import json


def config_reader(content_to_return: str) -> dict:
    j = json.load(open("config.json", 'r'))
    return j[content_to_return]
