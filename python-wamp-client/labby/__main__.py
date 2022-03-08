"""
Easy labby launch script
"""


import argparse
import json
from os import getenv, path
from labby import run_router
import labby.prompty as prompty

if __name__ == '__main__':

    CONFIG_PATH = "./.labby_config.json"
    config = {
        "backend_url": "ws://localhost:20408/ws",
        "backend_realm": "realm1",
        "frontend_url": "ws://localhost:8083/ws",
        "frontend_realm": "frontend",
        "exporter" : None
    }

    if path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as config_file:
            try:
                config = json.loads(config_file.read())
            except json.JSONDecodeError as error:
                print("Got JSONDecodeError while trying to decode config: ", error)
            except IOError as error:
                print("Got IOError while trying to decode config: ", error)
    else:
        config["backend_url"] = getenv(
            "LABBY_BACKEND_URL",   config["backend_url"])
        config["backend_realm"] = getenv(
            "LABBY_BACKEND_REALM", config["backend_realm"])
        config["frontend_url"] = getenv(
            "LABBY_FRONTEND_URL",  config["frontend_url"])
        config["frontend_realm"] = getenv(
            "LABBY_FRONTEND_REALM", config["frontend_realm"])
        config["exporter"] = getenv("LABBY_EXPORTER")

    parser = argparse.ArgumentParser(
        description='Launch Labgrid-frontend Router')
    parser.add_argument('--backend_url', type=str, required=False)
    parser.add_argument('--backend_realm', type=str, required=False)
    parser.add_argument('--frontend_url', type=str, required=False)
    parser.add_argument('--frontend_realm', type=str, required=False)
    parser.add_argument('--exporter', type=str, required=False)
    parser.add_argument('--prompty', action='store_true', required=False)
    args = parser.parse_args()

    if args.backend_url is not None:
        config["backend_url"] = args.backend_url
    if args.backend_realm is not None:
        config["backend_realm"] = args.backend_realm
    if args.exporter is not None:
        config["exporter"] = args.exporter
    if args.prompty:
        prompty.run(**config)
    else:
        run_router(**config)
