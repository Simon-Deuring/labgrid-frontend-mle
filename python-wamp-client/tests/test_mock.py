"""
Mock tests for labby module
"""

import asyncio
import sys
import unittest
from datetime import datetime
from random import random
from typing import Callable, List, Union
from unittest import mock
from unittest.mock import MagicMock, patch

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

    @make_async
    def call(self, func_str: str, *args):
        if func_str in {"org.labgrid.coordinator.acquire_place", "org.labgrid.coordinator.release_place"}:
            return random() > 0.5
        if func_str == "org.labgrid.coordinator.get_places":
            return PLACES
        if func_str == "org.labgrid.coordinator.get_resources":
            return RESOURCES


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
        ret : Union[List[Place], LabbyError] = await rpc.places(context)
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
        place_name = place= list(PLACES.keys())[0]
        place = await rpc.fetch_places(context, place_name)
        assert place is not None
        assert not isinstance(place, LabbyError)
        assert place == {place_name:PLACES[place_name]}
        

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

    def test_on_join(self) -> None:
        """
        Test onJoin callback function, mock ApplicationSession Super class
        """
        # TODO test criteria
        client = LabbyClient()
        client.subscribe = mock.MagicMock()
        client.onJoin(details=None)

    def test_on_leave(self) -> None:
        """
        Test onLeave callback function, mock ApplicationSession Super class
        """
        # TODO test criteria
        client = LabbyClient()
        client.disconnect = mock.MagicMock()
        client.onLeave(details=None)

    def test_on_place_changed_changed(self) -> None:
        """
        Test onPlaceChanged callback function, mock ApplicationSession Super class
        """
        client = LabbyClient()
        assert PLACES is not None
        place_name, place = list(PLACES.items())[0]
        user = f"test{datetime.now()}"
        place['acquired'] = user
        asyncio.run(client.on_place_changed(name=place_name, place_data=place))
        assert client.places
        assert client.places[place_name]
        assert client.places[place_name]['acquired']
        assert user == client.places[place_name]['acquired']

    @async_test
    async def test_on_resource_changed_changed(self) -> None:
        """
        Test onResourceChanged callback function, mock ApplicationSession Super class
        """
        client = LabbyClient()
        assert RESOURCES is not None
        exporter = 'exporter2'
        await client.on_resource_changed(exporter=exporter, group_name='NetworkService', resource_name='NetworkService', resource_data=RESOURCES[exporter])
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

    def test_on_join(self) -> None:
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
        run_router("localhost", "realm1")


if __name__ == "__main__":
    unittest.main()
