"""
Easy labby launch script
"""

from labby import run_router

if __name__ == '__main__':
    import json
    from os import path
    from urllib.parse import urlsplit
    import argparse
    import sys

    CONFIG_PATH = "./.labby_config.json"

    if path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as config_file:
            try:
                content_json = json.loads(config_file.read())
            except json.JSONDecodeError as error:
                print("Got JSONDecodeError while trying to decode config: ", error)
            except IOError as error:
                print("Got IOError while trying to decode config: ", error)

    config = {
        "url": u"ws://localhost:20408/ws",
        "realm": "realm1"
    }

    parser = argparse.ArgumentParser(description='Launch Labgrid-frontend Router')
    parser.add_argument('--url', type=str, required=False)
    parser.add_argument('--realm', type=str, required=False)
    args = parser.parse_args()

    if not args.url is None:
        config["url"] = args.url
    if not args.realm is None:
        config["realm"] = args.realm

    URL = config["url"]
    REALM = config["realm"]
    PORT = urlsplit(URL).port
    PORT = PORT if not PORT is None else 80
    run_router(URL, REALM)
