"""
Easy labby launch script
"""


import argparse
import json
from os import getenv, path
from os.path import expanduser
from labby import run_router
import labby.prompty as prompty

if __name__ == '__main__':

    CONFIG_PATH = "./.labby_config.json"
    config = {
        "backend_url": "ws://localhost:20408/ws",
        "backend_realm": "realm1",
        "frontend_url": "ws://localhost:8083/ws",
        "frontend_realm": "frontend",
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
        config["keyfile_path"] = getenv(
            "LABBY_KEYFILE_PATH", "")
        config["remote_url"] = getenv(
            "LABBY_KEYFILE_PATH", "")

    parser = argparse.ArgumentParser(
        description='Launch Labgrid-frontend Router')
    parser.add_argument('--backend_url', type=str, required=False)
    parser.add_argument('--backend_realm', type=str, required=False)
    parser.add_argument('--frontend_url', type=str, required=False)
    parser.add_argument('--frontend_realm', type=str, required=False)
    parser.add_argument('--prompty', action='store_true', required=False)
    parser.add_argument('--keyfile_path', type=str, required=False)
    parser.add_argument('--remote_url', type=str, required=False)
    args = parser.parse_args()
    if args.backend_url:
        config['backend_url'] = args.backend_url
    if args.backend_realm:
        config['backend_realm'] = args.backend_realm
    if args.frontend_url:
        config['frontend_url'] = args.frontend_url
    if args.frontend_realm:
        config['frontend_realm'] = args.frontend_realm
    if args.prompty:
        config['prompty'] = args.prompty
    if args.remote_url:
        config['remote_url'] = args.remote_url
    if args.keyfile_path:
        if "~" in args.keyfile_path:
            args.keyfile_path = expanduser(args.keyfile_path)
        config['keyfile_path'] = args.keyfile_path

    if config.get('prompty', None):
        del config['prompty']
        prompty.run(**config)
    else:
        run_router(**config)
