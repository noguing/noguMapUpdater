from sys import argv
from loguru import logger


if __name__ == "__main__":
    try:
        cmd = argv[1]
        if cmd == "update":
            try:
                from packages.update_cycle import update_new
                from time import sleep
                while True:
                    n = 60
                    for _ in range(60):
                        print(f"{n}秒后开始检测更新", end="\r")
                        sleep(1)
                        n -= 1
                    update_new()
            except Exception as e:
                logger.error(e)
        elif cmd == "initget":
            from packages.map_sid_getter import run_map_get
            run_map_get()
        elif cmd == "help":
            print(
                "\nhelp:\n"
                "  args:\n"
                "    update : \"Start map update. Must be used after initget.\"\n"
                "    initget: \"Get all maps from ppy and save them to file or mongodb(depend on your config).\"\n"
                "    help： \"Show this document.\"\n"
            )
    except Exception:
        print("Something went wrong, "
              "please run \"python {this_file}.py help\"or \"python3 {this_file}.py help\" to show help.")
