"""
A wamp client which registers a rpc function
"""
import asyncio
import asyncio.log
import getpass
import logging
import os
from getpass import getuser as _getuser
from os import getenv
from socket import gethostname as _gethostname
from time import sleep
from typing import Callable, Dict, List, Optional

import autobahn.wamp.exception as wexception
from autobahn.asyncio.wamp import ApplicationRunner, ApplicationSession

from .labby_ssh import Session as SSHSession
from .labby_ssh import parse_hostport
from .labby_types import (ExporterName, GroupName, PlaceName, ResourceName,
                          Session)
from .router import Router
from .rpc import (acquire, acquire_resource, add_match, cancel_reservation,
                  console, console_close, console_write, create_place,
                  create_reservation, create_resource, del_match, delete_place,
                  delete_resource, forward, get_alias, get_exporters,
                  get_reservations, info, invalidates_cache, list_places,
                  places, places_names, poll_reservation, power_state,
                  refresh_reservations, release, release_resource, resource,
                  resource_by_name, resource_names, resource_overview)

labby_sessions: List["LabbyClient"] = []
frontend_sessions: List["RouterInterface"] = []


def gethostname():
    return os.environ.get('LABBY_HOSTNAME', _gethostname())


def getuser():
    return os.environ.get('LABBY_USERNAME', _getuser())


class LabbyClient(Session):
    """
    Specializes Application Session to handle Communication
    specifically with the labgrid-frontend and the labgrid coordinator
    """

    def __init__(self, config):
        # make sure only one active labby client exists
        self.user_name = f"{gethostname()}/{getuser()}"
        self.frontend = config.extra.get('frontend')
        self.frontend.labby = self
        self.ssh_session = config.extra.get('ssh_session')

        super().__init__(config=config)
        labby_sessions.append(self)

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
                       "org.labgrid.coordinator.place_changed")
        self.subscribe(self.on_resource_changed,
                       "org.labgrid.coordinator.resource_changed")
        asyncio.create_task(refresh_reservations(self))

    def onLeave(self, details):
        self.log.info("Coordinator session disconnected.")
        self.disconnect()
        labby_sessions.remove(self)

    @invalidates_cache('power_states')
    async def on_resource_changed(self,
                                  exporter: ExporterName,
                                  group_name: GroupName,
                                  resource_name: ResourceName,
                                  resource_data: Dict):
        """
        Listen on resource changes on coordinator and update cache on changes
        """
        res = {exporter: {group_name: {resource_name: resource_data}}}
        if self.resources.get_soft() is None:
            self.resources._data = res

        if exporter not in self.resources.get_soft():
            self.resources.get_soft()[exporter] = {
                group_name: {resource_name: resource_data}}
        else:
            self.resources.get_soft()[exporter].get(group_name, {}).update(
                {resource_name: resource_data})

        if resource_name not in self.resources.get_soft()[exporter][group_name]:
            self.log.info(
                f"Resource {exporter}/{group_name}/{resource_name} created.")
        elif resource_data:
            self.log.info(
                f"Resource {exporter}/{group_name}/{resource_name} changed:")
        else:
            self.log.info(
                f"Resource {exporter}/{group_name}/{resource_name} deleted")

        self.power_states = None  # Invalidate power state cache
        if self.frontend:
            self.frontend.publish("localhost.onResourceChanged",
                                  self.resources.get_soft()[exporter][group_name][resource_name])

    @invalidates_cache('power_states')
    async def on_place_changed(self, name: PlaceName, place_data: Optional[Dict] = None):
        """
        Listen on place changes on coordinator and update cache on changes
        """
        if self.places.get_soft() is not None and not place_data:
            del self.places[name]
            self.log.info(f"Place {name} deleted")
            return

        if self.places.get_soft() is None:
            self.places._data = {}

        if name not in self.places.get_soft():
            self.places.get_soft()[name] = place_data
            self.log.info(f"Place {name} created.")
        else:
            place = self.places.get_soft()[name]
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

        if self.frontend:
            self.frontend.publish("localhost.onPlaceChanged", place_data)


class RouterInterface(ApplicationSession):
    """
    Wamp router, for communicaion with frontend
    """

    def _labby_callback(self):
        return self.labby

    def __init__(self, config):
        globals()["FRONTEND_REF"] = self
        self.backend_url = config.extra.get("backend_url")
        self.backend_realm = config.extra.get("backend_realm")
        self.keyfile_path = config.extra.get("keyfile_path")
        self.remote_url = config.extra.get("remote_url")
        self.labby = None
        super().__init__(config=config)
        frontend_sessions.append(self)

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
            return await procedure(self._labby_callback(), *args, *o_args)
        func = bind
        self.log.info(f"Registered function for endpoint {endpoint}.")
        try:
            super().register(func, endpoint)
        except wexception.Error as err:
            self.log.error(
                f"Could not register procedure: {err}.\n{err.with_traceback(None)}")

    async def onJoin(self, details):
        self.log.info("Joined Frontend Session.")
        # asyncio.get_event_loop().call_soon(self._start_labby)
        asyncio.get_event_loop().run_in_executor(None, _start_labby, self.remote_url,
                                                 self.backend_url, self.backend_realm, self.keyfile_path, self)

        # wait unitl labby startup is done
        while self.labby is None:
            await asyncio.sleep(.5)

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
        self.register("console", console)
        self.register("console_write", console_write)
        self.register("console_close", console_close)

    def onLeave(self, details):
        self.log.info("Session disconnected.")
        self.disconnect()
        frontend_sessions.remove(self)


def _start_labby(remote_url, backend_url, backend_realm, keyfile_path, frontend_client):
    """
    run labby and ssh session manager. wait for password if not provided in
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    remote_host, remote_port, user = parse_hostport(remote_url)
    assert remote_host and remote_port and user
    ssh_session = SSHSession(host=remote_host,
                             port=remote_port,
                             username=user,
                             keyfile_path=keyfile_path)
    if (password := getenv('LABBY_SSH_PASSWORD', None)) is None:
        password = getpass.getpass(
            f"Password for: {remote_url}:\n")
    ssh_session.open(password)
    # local_port = parse_hostport(backend_url)[1]
    asyncio.get_event_loop().run_in_executor(
        None, ssh_session.forward, 20408, 'localhost', 20408)

    def start():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.log.logger.info(
            "Connecting to %s on realm '%s'", backend_url, backend_realm)
        # start ssh session
        labby_runner = ApplicationRunner(backend_url,
                                         realm=backend_realm,
                                         extra={'frontend': frontend_client,
                                                'ssh_session': ssh_session})
        labby_coro = labby_runner.run(LabbyClient, start_loop=False)
        assert labby_coro is not None
        loop.run_until_complete(labby_coro)
        loop.run_forever()

    # Thread(target=start, name=f'{remote_url}-labby').start()
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, start)


def run_router(backend_url: str,
               backend_realm: str,
               frontend_url: str,
               frontend_realm: str,
               keyfile_path: str,
               remote_url: str):
    """
    Connect to labgrid coordinator and start local crossbar router
    """
    loop = asyncio.get_event_loop()
    logging.basicConfig(
        level="INFO", format="%(asctime)s [%(name)s][%(levelname)s] %(message)s")

    frontend_runner = ApplicationRunner(
        url=frontend_url, realm=frontend_realm,
        extra={"backend_url": backend_url, "backend_realm": backend_realm, "keyfile_path": keyfile_path, "remote_url": remote_url})
    frontend_coro = frontend_runner.run(RouterInterface, start_loop=False)

    asyncio.log.logger.info(
        "Starting Frontend Router on url %s and realm %s", frontend_url, frontend_realm)
    router = Router("labby/router/.crossbar")
    sleep(4)
    assert frontend_coro is not None
    try:
        loop.run_until_complete(frontend_coro)
        loop.run_forever()
    except ConnectionRefusedError as err:
        asyncio.log.logger.error(err.strerror)
    except KeyboardInterrupt:
        pass
    finally:
        frontend_coro.close()
        router.stop()
