"""
A wamp client which registers a rpc function
"""
from typing import Dict, Callable

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

from . import rpc

class RPC():
    """
    Wrapper for remote procedure call functions
    """

    def __init__(self, endpoint: str, func: Callable):
        assert not endpoint is None
        assert not func is None
        self.endpoint = endpoint
        self.func = func

    def __repr__(self):
        from inspect import signature

        sig = signature(self.func)
        ret_type = sig.return_annotation
        params = sig.parameters
        return f"{self.endpoint}\
            ({', '.join([f'{x.name}:{x.annotation}'for x in params.values()])}) -> {ret_type}"

    def bind(self, *args, **kwargs):
        """
        Bind RPC to specific context, e.g LabbyClient Session, or pass immutables into func
        """
        return lambda *a, **kw: self.func( *args, *a, **kwargs, **kw)


LOADED_RPC_FUNCTIONS: Dict[str, RPC]


class LabbyClient(ApplicationSession):
    """
    Specializes Application Session to handle Communication specifically with the labgrid-frontend and the labgrid coordinator
    """
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
            # TODO (Kevin) handle other authentication methods
            self.log.error(
                "Only Ticket authentication enabled, atm. Aborting...")
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

    def onJoin(self, details):
        self.log.info("Joined Session.")

        try:
            self.register("places",)
            self.register("resource", target='cup')
        except Exception as err:
            self.log.error(f"Could not register procedure: {err}.\n{err.with_traceback()}")

    def onLeave(self, details):
        self.log.info("Session disconnected.")
        self.disconnect()


def run_router(url: str, realm: str):
    """
    Connect to labgrid coordinator and start local crossbar router
    """
    global LOADED_RPC_FUNCTIONS
    LOADED_RPC_FUNCTIONS = {
        "places":   RPC("localhost.places", rpc.places),
        "resource": RPC("localhost.resource", rpc.resource)
    }
    runner = ApplicationRunner(url=url, realm=realm, extra=None)
    try:
        print(f"Connecting to {url} on realm {realm}")
        runner.run(LabbyClient)
    except ConnectionRefusedError as err:
        from sys import stderr
        print(err.strerror,file=stderr)
