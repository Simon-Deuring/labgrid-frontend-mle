"""
A wamp client which registers a rpc function
"""
from typing import Callable, Dict, Optional  
from time import sleep

import logging
import asyncio
import asyncio.log
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
import autobahn.wamp.exception as wexception

from .rpc import forward, places, reservations, resource, power_state, acquire, release, info, resource_by_name, resource_overview
from .router import Router
from .labby_types import GroupName, PlaceName, ResourceName, Session

CALLBACK_REF: Optional[ApplicationSession] = None


def get_context_callback():
    """
    If context takes longer to create, prevent Context to be None in Crossbar router context
    """
    return globals()["CALLBACK_REF"]


class LabbyClient(Session):
    """
    Specializes Application Session to handle Communication
    specifically with the labgrid-frontend and the labgrid coordinator
    """

    def __init__(self, config=None):
        # make sure only one active labby client exists
        assert "CALLBACK_REF" not in globals() or globals()["CALLBACK_REF"] is None
        globals()["CALLBACK_REF"] = self
        super().__init__(config=config)

    def onConnect(self):
        self.log.info(
            f"Connected to Coordinator, joining realm '{self.config.realm}'")
        # TODO load from config or get from frontend
        self.join(self.config.realm, ['ticket'], authid='client/labby/dummy')

    def onChallenge(self, challenge):
        self.log.info("Authencticating.")
        if challenge.method == 'ticket':
            return ""  # don't provide a password
        self.log.error(
            "Only Ticket authentication enabled, atm. Aborting...")
        raise NotImplementedError(
            "Only Ticket authentication enabled, atm")

    def onJoin(self, details):
        self.log.info("Joined Coordinator Session.")
        self.subscribe(self.on_place_changed,
                       u"org.labgrid.coordinator.place_changed")
        self.subscribe(self.on_resource_changed,
                       u"org.labgrid.coordinator.resource_changed")

    def onLeave(self, details):
        self.log.info("Coordinator session disconnected.")
        self.disconnect()

    async def on_resource_changed(self,
                                  exporter: str,
                                  group_name: GroupName,
                                  resource_name: ResourceName,
                                  resource_data: Dict):
        """
        Listen on resource changes on coordinator and update cache on changes
        """
        # group = self.resources.setdefault(exporter,{}).setdefault(group_name, {})
        group = self.resources if self.resources is not None else {}
        # Do not replace the ResourceEntry object, as other components may keep
        # a reference to it and want to see changes.
        old = None if resource_name not in group else group[resource_name]
        group[resource_name] = resource_data
        if resource_data and not old:
            self.log.info(
                # f"Resource {exporter}/{group_name}/{resource_name} created: {resource_data}")
                f"Resource {exporter}/{group_name}/{resource_name} created.")
        elif resource_data:
            self.log.info(
                f"Resource {exporter}/{group_name}/{resource_name} changed:")
        else:
            self.log.info(
                f"Resource {exporter}/{group_name}/{resource_name} deleted")
        self.power_states = None # Invalidate power state cache


    async def on_place_changed(self, name: PlaceName, place_data: Dict):
        """
        Listen on place changes on coordinator and update cache on changes
        """
        if self.places is not None and not place_data:
            del self.places[name]
            self.log.info("Place {} deleted", name)

        if self.places is None:
            self.places = {}

        if name not in self.places:
            self.places[name] = place_data
            # self.log.info("Place {} created: {}", name, place)
            self.log.info(f"Place {name} created.")
        else:
            place = self.places[name]
            # old = flat_dict(place.asdict())
            place.update(place_data)
            # new = flat_dict(place.asdict())
            self.log.info(f"Place {name} changed:")
            # for k, v_old, v_new in diff_dict(old, new):
            #     print(f"  {k}: {v_old} -> {v_new}")
        self.power_states = None # Invalidate power state cache



class RouterInterface(ApplicationSession):
    """
    Wamp router, for communicaion with frontend
    """

    def __init__(self, config=None):
        if config and 'exporter' in config.extra:
            self.exporter = config.extra['exporter']
        super().__init__(config)

    def onConnect(self):
        self.log.info(
            f"Connected to Coordinator, joining realm '{self.config.realm}'")
        self.join(self.config.realm)

    def register(self, func_key: str, procedure: Callable, *args):
        """
        Register functions from RPC store from key, overrides ApplicationSession::register
        """
        endpoint = f"localhost.{func_key}"

        async def bind(*a):
            return await procedure(get_context_callback(), *args, *a)
        func = bind
        self.log.info(f"Registered function for endpoint {endpoint}.")
        super().register(func, endpoint)

    def onJoin(self, details):
        self.log.info("Joined Frontend Session.")
        try:
            self.register("places", places)
            self.register("resource", resource, self.exporter)
            self.register("power_state", power_state, self.exporter)
            self.register("acquire", acquire)
            self.register("release", release)
            self.register("reservations", reservations)
            self.register("resource_overview", resource_overview)
            self.register("resource_by_name", resource_by_name)
            self.register("info", info)
            self.register("forward", forward)
        except wexception.Error as err:
            self.log.error(
                f"Could not register procedure: {err}.\n{err.with_traceback(None)}")

    def onLeave(self, details):
        self.log.info("Session disconnected.")
        self.disconnect()


def run_router(backend_url: str, backend_realm: str, frontend_url: str, frontend_realm: str, exporter: str):
    """
    Connect to labgrid coordinator and start local crossbar router
    """

    globals()["LOADED_RPC_FUNCTIONS"] = {}
    logging.basicConfig(
        level="DEBUG", format="%(asctime)s [%(name)s][%(levelname)s] %(message)s")

    labby_runner = ApplicationRunner(
        url=backend_url, realm=backend_realm, extra=None)
    labby_coro = labby_runner.run(LabbyClient, start_loop=False)
    frontend_runner = ApplicationRunner(
        url=frontend_url, realm=frontend_realm, extra={"exporter": exporter})
    frontend_coro = frontend_runner.run(RouterInterface, start_loop=False)

    asyncio.log.logger.info(
        "Starting Frontend Router on url %s and realm %s", frontend_url, frontend_realm)
    router = Router("labby/router/.crossbar")
    sleep(5)
    loop = asyncio.get_event_loop()
    assert labby_coro is not None
    assert frontend_coro is not None
    try:

        asyncio.log.logger.info(
            "Connecting to %s on realm '%s'", backend_url, backend_realm)
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
