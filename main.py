import multiprocessing
from packages.map_sid_getter_playwright import run as run_explore_ppy_maps
from playwright.sync_api import sync_playwright
from startTokenUpdateCycle import cycle as token_cycle
from startMapUpdateCycle import cycle as map_update_cycle
from sys import argv


if __name__ == "__main__":
    try:
        cmd = argv[1]
        if cmd == "traverse-map":
            with sync_playwright() as playwright:
                run_explore_ppy_maps(playwright)
        elif cmd == "cycle":
            # creating processes
            p1 = multiprocessing.Process(target=map_update_cycle, args=())
            p2 = multiprocessing.Process(target=token_cycle, args=())

            # starting process 1&2
            p1.start()
            p2.start()

            # wait until process 1&2 is finished
            p1.join()
            p2.join()
        elif cmd == "help":
            print(
                "help:"
                "  args:"
                "    traverse-map : \"start getting map from ppy (through playwright)(low success rate).\""
                "    cycle: \"start cycle token updating and token updating.\""
                "    help： \"show this document.\""
            )
    except Exception:
        print("Something went wrong, "
              "please run \"python {this_file}.py help\"or \"python3 {this_file}.py help\" to show help.")
