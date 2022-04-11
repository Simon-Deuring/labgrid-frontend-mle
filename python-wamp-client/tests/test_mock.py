"""
Mock tests for labby module
"""

import asyncio
import sys
import unittest
from datetime import datetime
from random import choice, random
from typing import Callable, Dict, List, Union
from unittest import mock
from unittest.mock import MagicMock, patch
from uuid import uuid4

import yaml
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

from labby.labby import LabbyClient, RouterInterface, run_router
from labby.labby_error import ErrorKind, LabbyError
from labby.labby_types import Place, PowerState, SerLabbyError, Session
from labby import rpc

PLACES = None
with open("tests/places.yaml", 'r') as file:
    PLACES = list(yaml.load_all(file, yaml.loader.FullLoader))[0]

RESOURCES = None
with open("tests/resources.yaml", 'r') as file:
    RESOURCES = list(yaml.load_all(file, yaml.loader.FullLoader))[0]


def make_async(func: Callable):
    """
    wrap a function with a future to make it async
    """
    def wrapper(*args, **kwargs):
        future = asyncio.Future()
        future.set_result(func(*args, **kwargs))
        return future
    return wrapper


def async_test(func):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(func)
        future = coro(*args, **kwargs)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(future)
    return wrapper


def mock_labby(func_names: List[str]):
    """
    monkey patch provided funcs from rpc module
    """
    def decorator(func):
        def wrapped(*args, **kwargs):
            temp = {}
            for rpc_func in func_names:
                assert rpc.__dict__[rpc_func]
                assert callable(rpc.__dict__[rpc_func])
                assert sys.modules[__name__].__dict__[rpc_func]
                assert callable(sys.modules[__name__].__dict__[rpc_func])
                temp[rpc_func] = (rpc.__dict__[rpc_func])
                rpc.__dict__[
                    rpc_func] = sys.modules[__name__].__dict__[rpc_func]
            ret = func(*args, **kwargs)
            for name, rpc_func in temp.items():
                rpc.__dict__[name] = rpc_func
            return ret

        return wrapped
    return decorator


class MockSession(Session):
    def __init__(self, *args, **kwargs) -> None:
        self.user_name = "client/labby/dummy"
        super().__init__(*args, **kwargs)

    @make_async
    def call(self, func_str: str, *args, **kwargs):
        if func_str in {"org.labgrid.coordinator.acquire_place", "org.labgrid.coordinator.release_place"}:
            return random() > 0.5
        if func_str == "org.labgrid.coordinator.get_places":
            return PLACES
        if func_str == "org.labgrid.coordinator.get_resources":
            return RESOURCES
        if func_str == "org.labgrid.coordinator.get_reservations":
            return {'token1': {'owner': 'labby/test', 'state': 'waiting', 'prio': 0.0, 'filters': {'main': {'name': 'place1'}}, 'allocations': {}, 'created': 1.0, 'timeout': 2.0}}
        if func_str == "org.labgrid.coordinator.create_reservation":
            prio = 0.0 if 'prio' not in kwargs else kwargs['prio']
            place = args[0].split("=")[1].strip()
            return {place: {'owner': 'labby/test', 'state': 'waiting', 'prio': prio, 'filters': {'main': {'name': place}}, 'allocations': {}, 'created': 1.0, 'timeout': 2.0}}
        if func_str == "org.labgrid.coordinator.cancel_reservation":
            return True
        if func_str == "org.labgrid.coordinator.poll_reservation":
            token = args[0]
            return {token: {'owner': 'labby/test', 'state': 'waiting', 'prio': 0.0, 'filters': {'main': {'name': token}}, 'allocations': {}, 'created': 1.0, 'timeout': 2.0}}


class TestAcquireRelease(unittest.TestCase):
    """
    Mock test acquire release rpcs
    """

    @async_test
    async def test_acquire(self):
        context = MockSession()
        #############
        ret = await rpc.acquire(context, 'place1')
        assert isinstance(ret, bool)

    @async_test
    async def test_release(self):
        context = MockSession()
        #############
        ret = await rpc.acquire(context, 'place1')
        assert isinstance(ret, bool)


class TestResources(unittest.TestCase):
    """
    test resource rpc calls
    """
    # @mock_labby(["fetch_resources"])
    @async_test
    async def test_resources_all(self):
        """
        test fetch all resources
        """
        context = MockSession()
        #############
        ret = await rpc.resource(context)
        assert isinstance(ret, dict)
        assert ret


class TestPlaces(unittest.TestCase):
    """
    Test cases for place rpcs
    """
    @async_test
    async def test_places_all(self):
        """
        test places, fetch all
        """
        context = MockSession()
        assert PLACES
        #############
        ret: Union[List[Place], LabbyError] = await rpc.places(context)
        assert ret is not None
        assert isinstance(
            ret, list), "Returned Value has to be valid, which means of type list."
        # check all places are returned
        for place in PLACES:
            assert place in [pl['name'] for pl in ret]

    @async_test
    async def test_places_individual(self):
        """
        test places fetch specific
        """
        context = MockSession()
        assert PLACES
        #############
        for place in PLACES:
            ret = await rpc.places(context, place)
            assert ret is not None
            assert isinstance(
                ret, list), "Returned Value has to be valid, which means of type list."
            assert ret[0]["name"] == place, "Only one place should match, which should be the original place"

    @async_test
    async def test_places_fail_exist(self):
        """
        test places, fetch fails, place does not exist
        """
        context = MockSession()
        #############
        ret = await rpc.places(context, "this place does not exist")
        assert ret is not None
        assert isinstance(
            ret, SerLabbyError), "rpc.places's return object should have been LabbyError serialized"
        assert ret["error"] is not None, "Not an error object"
        assert ret["error"]["kind"] == ErrorKind.NOT_FOUND.value, "Not the right error object"

    @async_test
    async def test_fetch_places(self):
        """
        test fetch places
        """
        ### place is None
        context = MockSession()
        places = await rpc.fetch_places(context, place=None)
        assert places is not None
        assert not isinstance(places, LabbyError)
        assert places == PLACES
        ### place is not None
        context = MockSession()
        assert PLACES
        place_name = list(PLACES.keys())[0]
        place = await rpc.fetch_places(context, place_name)
        assert place is not None
        assert not isinstance(place, LabbyError)
        assert place == {place_name: PLACES[place_name]}

    @staticmethod
    @make_async
    def _context_fetch_places_fail(_, place=None):
        return None

    @async_test
    @patch('autobahn.asyncio.wamp.ApplicationSession.call', _context_fetch_places_fail)
    async def test_fetch_places_fails(self):
        """
        test fetch places
        """
        context = Session()
        places = await rpc.fetch_places(context, place=None)
        assert places is not None
        assert isinstance(places, LabbyError)
        assert places.kind == ErrorKind.NOT_FOUND

        context = Session()
        places = await rpc.fetch_places(context, place='mle-lg-ref-1')
        assert places is not None
        assert isinstance(places, LabbyError)
        assert places.kind == ErrorKind.NOT_FOUND


class TestPowerState(unittest.TestCase):
    """
    Test cases for power state rpcs
    """

    @async_test
    async def test_power_states(self):
        """
        test the powerstate of a place
        """
        context = MockSession()
        assert PLACES is not None
        for place in list(PLACES.keys()):
            #############
            ret = await rpc.power_state(context, place)
            assert ret
            assert isinstance(ret, PowerState)
            assert isinstance(ret["power_state"], bool)

    @async_test
    async def test_power_states_place_fail(self):
        """
        test the powerstate of a place
        """
        context = MockSession()
        #############
        ret = await rpc.power_state(context, "this place does not exist")
        assert ret, "rpc.power_state did not return a proper return object"
        assert isinstance(
            ret, SerLabbyError), "rpc.powerstate's return object should have been LabbyError serialized"
        assert ret["error"] is not None, "Not an error object"
        assert ret["error"]["kind"] == ErrorKind.NOT_FOUND.value, "Not the right error object"


class TestLabby(unittest.TestCase):
    """
    mock test labby
    """
    @async_test
    @patch("asyncio.create_task")
    @patch.object(ApplicationSession, "call", make_async(MagicMock()))
    async def test_on_join(self, ct) -> None:
        """
        Test onJoin callback function, mock ApplicationSession Super class
        """
        # TODO test criteria
        client = LabbyClient()
        client.subscribe = mock.MagicMock()
        await client.onJoin(details=None)

    def test_on_leave(self) -> None:
        """
        Test onLeave callback function, mock ApplicationSession Super class
        """
        # TODO test criteria
        client = LabbyClient()
        client.disconnect = mock.MagicMock()
        client.onLeave(details=None)

    @async_test
    @patch.object(ApplicationSession, "publish")
    async def test_on_place_changed(self, publish) -> None:
        """
        Test onPlaceChanged callback function, mock ApplicationSession Super class
        """
        client = LabbyClient()
        assert PLACES is not None
        place_name, place = list(PLACES.items())[0]
        user = f"test{datetime.now()}"
        place['acquired'] = user
        await client.on_place_changed(name=place_name, place_data=place)
        assert client.places
        assert client.places[place_name]
        assert client.places[place_name]['acquired']
        assert user == client.places[place_name]['acquired']

    @async_test
    @patch("labby.get_frontend_callback")
    @patch.object(ApplicationSession, 'publish')
    async def test_on_resource_changed(self, obj, c) -> None:
        """
        Test onResourceChanged callback function, mock ApplicationSession Super class
        """
        client = LabbyClient()
        assert RESOURCES is not None
        exporter = 'exporter2'
        await client.on_resource_changed(exporter=exporter, group_name='NetworkService', resource_name='NetworkService', resource_data=RESOURCES['exporter1'])
        assert client.resources
        assert client.resources['exporter2'] is not None
        # TODO create
        # test once onResourceChanged is done

    def test_on_challenge(self) -> None:
        """
        Test onChallenge callback function, mock ApplicationSession Super class
        """
        client = LabbyClient()
        challenge = MagicMock(method='ticket')
        response = client.onChallenge(challenge)
        assert "" == response
        try:
            challenge = MagicMock(method='anything else')
        except NotImplementedError:
            pass
        # TODO create test once onResourceChanged is done

    def test_on_connect(self) -> None:
        """
        Test onConnect callback function, mock ApplicationSession Super class
        """
        client = LabbyClient()
        client.join = MagicMock()

        client.onConnect()

# TODO check returned values and call args


class TestFrontendRouter(unittest.TestCase):
    """
    mock test labby frontend router
    """

    def test_on_connect(self) -> None:
        """
        Test onConnect callback function, mock ApplicationSession Super class
        """
        client = RouterInterface()
        client.join = MagicMock()

        client.onConnect()

    def test_on_leave(self) -> None:
        """
        Test onLeave callback function, mock ApplicationSession Super class
        """
        # TODO test criteria
        client = RouterInterface()
        client.disconnect = mock.MagicMock()
        client.onLeave(details=None)

    @patch("asyncio.create_task")
    @patch.object(ApplicationSession, "call", make_async(MagicMock()))
    def test_on_join(self, ct) -> None:
        client = RouterInterface()
        client.register = MagicMock()
        client.onJoin(details=None)
        # no exceptions

    @patch.object(ApplicationSession, 'register')
    def test_register(self, register: MagicMock):
        client = RouterInterface()
        func_key = "test"
        procedure = MagicMock()
        client.register(func_key, procedure, 'arg1')

        assert len(register.call_args) == 2
        arg_endpoint: MagicMock = register.call_args[1]
        # TODO check correctness


class TestStartRouter(unittest.TestCase):
    @staticmethod
    async def _run(*args, **kwargs):
        fut = asyncio.Future()
        fut.set_result(MagicMock()(*args, kwargs))
        return fut

    @patch('asyncio.get_event_loop')
    @patch('subprocess.run', _run)
    @patch.object(ApplicationRunner, 'run')
    def test_start(self, run, loop):
        run_router(backend_url="ws://localhost:20408/ws",
                   backend_realm="realm1", frontend_url="ws://localhost:8083/ws", frontend_realm="frontend", exporter="exporter")


class TestReservation(unittest.TestCase):

    @async_test
    async def test_create_reservations(self):
        context = MockSession()
        registration = await rpc.create_reservation(context, "place2")
        assert registration
        assert isinstance(registration, Dict)
        assert next(iter(registration.values()))[
            'filters']['main']['name'] == 'place2'

    @async_test
    async def test_create_already_exists(self):
        context = MockSession()
        registration = await rpc.create_reservation(context, "place2")
        assert registration
        assert isinstance(registration, Dict)
        registration = next(iter(registration.values()))
        assert registration['filters']['main']['name'] == 'place2'
        registration = await rpc.create_reservation(context, 'place2')
        assert registration
        assert isinstance(registration, SerLabbyError)
        assert registration['error']['kind'] == ErrorKind.FAILED.value

    @async_test
    async def test_get_reservation(self):
        context = MockSession()
        # !notice mock session will add a 'place1' on get_reservations
        ret = await rpc.create_reservation(context, "place2")
        assert ret
        assert isinstance(ret, Dict)
        reservations = await rpc.get_reservations(context)
        assert reservations
        assert isinstance(reservations, dict)

    @async_test
    async def test_cancel_reservation(self):
        context = MockSession()
        await rpc.create_reservation(context, "place2")
        cancel = await rpc.cancel_reservation(context, "place2")
        assert isinstance(cancel, bool)

    @async_test
    async def test_cancel_reservation_fail(self):
        context = MockSession()
        cancel = await rpc.cancel_reservation(context, "place2")
        assert isinstance(cancel, SerLabbyError)
        assert cancel['error']['kind'] == ErrorKind.FAILED.value

    @async_test
    async def test_poll_reservation(self):
        context = MockSession()
        await rpc.create_reservation(context, "place2")
        poll = await rpc.poll_reservation(context, "place2")
        assert isinstance(poll, Dict)
        assert 'error' not in poll


class TestCreateDelete(unittest.TestCase):
    @async_test
    async def test_create(self):
        context = MockSession()

        created = await rpc.create_place(context, f'test_place_create_{uuid4()}')
        assert not isinstance(
            created, SerLabbyError), "Create place call failed"


if __name__ == "__main__":
    unittest.main()
