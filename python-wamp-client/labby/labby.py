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

from .rpc import (acquire_resource, add_match, cancel_reservation, create_place, create_resource, del_match,
                  delete_place, delete_resource, forward, get_alias, get_exporters, invalidates_cache, list_places,
                  places, places_names, get_reservations, create_reservation, poll_reservation, refresh_reservations, release_resource, resource, power_state,
                  acquire, release, info, resource_by_name, resource_names, resource_overview)
from .router import Router
from .labby_types import GroupName, PlaceName, ResourceName, Session


def get_context_callback() -> Optional['LabbyClient']:
    """
    If context takes longer to create, prevent Context to be None in Crossbar router context
    """
    return globals().get("CALLBACK_REF", None)


def get_frontend_callback() -> Optional['RouterInterface']:
    """
    If context takes longer to create, prevent Context to be None in Crossbar router context
    """
    return globals().get("FRONTEND_REF", None)


class LabbyClient(Session):
    """
    Specializes Application Session to handle Communication
    specifically with the labgrid-frontend and the labgrid coordinator
    """

    def __init__(self, config=None):
        # make sure only one active labby client exists
        globals()["CALLBACK_REF"] = self
        self.user_name = "labby/dummy"
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

    async def onJoin(self, details):
        self.log.info("Joined Coordinator Session.")
        res = await self.call("wamp.registration.list")
        for proc in res['exact']:
            p = await self.call("wamp.registration.get", proc)
            print(p['uri'])
        res = await self.call("wamp.subscription.list")
        for proc in res['exact']:
            p = await self.call("wamp.subscription.get", proc)
            print(p['uri'])

        self.subscribe(self.on_place_changed,
                       "org.labgrid.coordinator.place_changed")
        self.subscribe(self.on_resource_changed,
                       "org.labgrid.coordinator.resource_changed")
        asyncio.create_task(refresh_reservations(self))
        # asyncio.run_coroutine_threadsafe(refresh_reservations(self), asyncio.get_event_loop())

    def onLeave(self, details):
        self.log.info("Coordinator session disconnected.")
        self.disconnect()

    @invalidates_cache('power_states')
    async def on_resource_changed(self,
                                  exporter: str,
                                  group_name: GroupName,
                                  resource_name: ResourceName,
                                  resource_data: Dict):
        """
        Listen on resource changes on coordinator and update cache on changes
        """
        if self.resources is None:
            self.resources = {}
        if exporter not in self.resources:
            self.resources[exporter] = {
                group_name: {resource_name: resource_data}}
        else:
            self.resources[exporter].get(group_name, {}).update(
                {resource_name: resource_data})

        if resource_name not in self.resources[exporter][group_name]:
            self.log.info(
                f"Resource {exporter}/{group_name}/{resource_name} created.")
        elif resource_data:
            self.log.info(
                f"Resource {exporter}/{group_name}/{resource_name} changed:")
        else:
            self.log.info(
                f"Resource {exporter}/{group_name}/{resource_name} deleted")

        self.power_states = None  # Invalidate power state cache
        if frontend := get_frontend_callback():
            frontend.publish("localhost.onResourceChanged",
                             self.resources[exporter][group_name][resource_name])

    @invalidates_cache('power_states')
    async def on_place_changed(self, name: PlaceName, place_data: Optional[Dict] = None):
        """
        Listen on place changes on coordinator and update cache on changes
        """
        if self.places is not None and not place_data:
            del self.places[name]
            self.log.info(f"Place {name} deleted")
            return

        if self.places is None:
            self.places = {}

        if name not in self.places:
            self.places[name] = place_data
            self.log.info(f"Place {name} created.")
        else:
            place = self.places[name]
            place.update(place_data)
            self.log.info(f"Place {name} changed.")
        if (  # add place to acquired places, if we have acquired it previously
            place_data
            and place_data['acquired'] is not None
            and place_data['acquired'] == self.user_name
            and name not in self.acquired_places
        ):
            self.acquired_places.add(name)
        if (
            place_data
            and name in self.acquired_places
            and place_data['acquired'] != self.user_name
        ):
            self.acquired_places.remove(name)

        if frontend := get_frontend_callback():
            frontend.publish("localhost.onPlaceChanged", place_data)



class RouterInterface(ApplicationSession):
    """
    Wamp router, for communicaion with frontend
    """

    def __init__(self, config=None):
        if config is not None and 'exporter' in config.extra:
            self.exporter = config.extra['exporter']
        globals()["FRONTEND_REF"] = self
        super().__init__(config=config)

    def onConnect(self):
        self.log.info(
            f"Connected to Coordinator, joining realm '{self.config.realm}'")
        self.join(self.config.realm)

    def register(self, func_key: str, procedure: Callable, *args):
        """
        Register functions from RPC store from key, overrides ApplicationSession::register
        """
        endpoint = f"localhost.{func_key}"

        async def bind(*o_args):
            return await procedure(get_context_callback(), *args, *o_args)
        func = bind
        self.log.info(f"Registered function for endpoint {endpoint}.")
        try:
            super().register(func, endpoint)
        except wexception.Error as err:
            self.log.error(
                f"Could not register procedure: {err}.\n{err.with_traceback(None)}")

    def onJoin(self, details):
        self.log.info("Joined Frontend Session.")

        self.register("places", places)
        self.register("list_places", list_places)
        self.register("resource", resource)
        self.register("power_state", power_state)
        self.register("acquire", acquire)
        self.register("release", release)
        self.register("resource_overview", resource_overview)
        self.register("resource_by_name", resource_by_name)
        self.register("info", info)
        self.register("forward", forward)
        self.register("create_place", create_place)
        self.register("delete_place", delete_place)
        self.register("get_reservations", get_reservations)
        self.register("create_reservation", create_reservation)
        self.register("cancel_reservation", cancel_reservation)
        self.register("poll_reservation", poll_reservation)
        self.register("create_resource", create_resource)
        self.register("delete_resource", delete_resource)
        self.register("place_names", places_names)
        self.register("get_alias", get_alias)
        self.register("get_exporters", get_exporters)
        self.register("acquire_resource", acquire_resource)
        self.register("release_resource", release_resource)
        self.register("resource_names", resource_names)
        self.register("add_match", add_match)
        self.register("del_match", del_match)


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
    sleep(4)
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
