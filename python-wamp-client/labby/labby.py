"""
A wamp client which registers a rpc function
"""
from typing import Dict
from time import sleep

import logging
import asyncio
import asyncio.log
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
import autobahn.wamp.exception as wexception

from . import rpc
from .rpc import RPC
from .router import Router


LOADED_RPC_FUNCTIONS: Dict[str, RPC]
CALLBACK_REF = None


def get_callback():
    return globals()["CALLBACK_REF"]


class LabbyClient(ApplicationSession):
    """
    Specializes Application Session to handle Communication specifically with the labgrid-frontend and the labgrid coordinator
    """

    def __init__(self, config: None):

        globals()["CALLBACK_REF"] = self
        super().__init__(config=config)

    def onConnect(self):
        self.log.info(
            f"Connected to Coordinator, joining realm '{self.config.realm}'")
        self.join(self.config.realm, ['ticket'], "public")

    def onChallenge(self, challenge):
        self.log.info("Authencticating.")
        # authid = "public"
        if challenge.method == 'ticket':
            return ""
        else:
            self.log.error("Only Ticket authentication enabled, atm. Aborting...")
            raise NotImplementedError(
                "Only Ticket authentication enabled, atm")

    def register(self, func_key: str, *args, **kwargs):
        """
        Register functions from RPC store from key, overrides ApplicationSession::register
        """
        assert not func_key is None
        func = LOADED_RPC_FUNCTIONS[func_key]
        self.log.info(f"Registered function for endpoint {func.endpoint}.")
        super().register(func.bind(self, *args, **kwargs), func.endpoint)

    async def onJoin(self, details):
        self.log.info("Joined Coordinator Session.")

    def onLeave(self, details):
        self.log.info("Coordinator session disconnected.")
        self.disconnect()


class RouterInterface(ApplicationSession):

    def onConnect(self):
        self.log.info(
            f"Connected to Coordinator, joining realm '{self.config.realm}'")
        self.join(self.config.realm)

    def register(self, func_key: str, *args, **kwargs):
        """
        Register functions from RPC store from key, overrides ApplicationSession::register
        """
        assert not func_key is None
        callback = LOADED_RPC_FUNCTIONS[func_key]
        endpoint = callback.endpoint
        func = callback.bind_frontend(get_callback, *args, **kwargs)
        self.log.info(f"Registered function for endpoint {endpoint}.")
        super().register(func, endpoint)

    def onJoin(self, details):
        self.log.info("Joined Frontend Session.")

        try:
            self.register("places")
            self.register("resource", target='cup')
            self.register("power_state", target='cup')
        except wexception.Error as err:
            self.log.error(f"Could not register procedure: {err}.\n{err.with_traceback()}")

    def onLeave(self, details):
        self.log.info("Session disconnected.")
        self.disconnect()


def run_router(url: str, realm: str):
    """
    Connect to labgrid coordinator and start local crossbar router
    """
    globals()['LOADED_RPC_FUNCTIONS'] = {
        "places":   RPC("localhost.places", rpc.places),
        "resource": RPC("localhost.resource", rpc.resource),
        "power_state": RPC("localhost.power_state", rpc.power_state)
    }

    logging.basicConfig(level="DEBUG", format="%(asctime)s [%(name)s][%(levelname)s] %(message)s")
    labby_runner = ApplicationRunner(url=url, realm=realm, extra=None)
    labby_coro = labby_runner.run(LabbyClient, start_loop=False)
    frontend_runner = ApplicationRunner(
        url='ws://localhost:8083/ws', realm='frontend', extra=None)
    frontend_coro = frontend_runner.run(RouterInterface, start_loop=False)

    asyncio.log.logger.info("Starting Frontend Router")
    router = Router("labby/router/.crossbar")
    sleep(5)
    loop = asyncio.get_event_loop()
    try:
        asyncio.log.logger.info(f"Connecting to {url} on realm {realm}")
        loop.run_until_complete(labby_coro)
        loop.run_until_complete(frontend_coro)
        loop.run_forever()
    except ConnectionRefusedError as err:
        asyncio.log.logger.error(err.strerror)
    except KeyboardInterrupt:
        pass
    finally:
        frontend_coro.close()
        labby_coro.close()
        asyncio.get_event_loop().close()
        router.stop()
