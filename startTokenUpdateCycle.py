import sched
import time
import json
from packages.getToken import get_token


schedule = sched.scheduler(time.time, time.sleep)


def token_update(inc):
    config = json.load(open("config.json", 'r'))["osu_client"]
    get_token(client_id=config["id"], client_secret=config["token"])
    schedule.enter(inc, 0, token_update, (inc,))


def cycle(inc=86400):
    schedule.enter(0, 0, token_update, (inc,))
    schedule.run()


if __name__ == "__main__":
    cycle(86400)  # 一天
