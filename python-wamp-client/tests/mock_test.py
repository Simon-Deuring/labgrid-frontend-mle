import yaml
from labby import rpc
from labby.labby_types import PlaceName, PowerState, Session
import asyncio
import sys
from typing import Callable, Dict, List, Optional, Union
import unittest
from unittest import mock
from labby.labby_error import LabbyError
sys.path.append(".")
sys.path.append("labby")


places: Optional[Dict] = None
with open("tests/places.yaml", 'r') as file:
    places = list(yaml.load_all(file, yaml.loader.FullLoader))


def make_async(f: Callable):
    def wrapper(*args, **kwargs):
        future = asyncio.Future()
        future.set_result(f(*args, **kwargs))
        return future
    return wrapper


@make_async
def fetch_places(context: Session, place: Optional[PlaceName]) -> Union[Dict, LabbyError]:
    global places
    place_data = map(
        lambda x: (x[0], {'name': x[0], **x[1]}),
        ((k, p) for ex in places for ex_name, place_data in ex.items()
         for k, p in place_data.items())
    )
    if place is not None:
        place_data = dict(filter(lambda item: item[1] == place, place_data))
    else:
        place_data = dict(place_data)
    return place_data


@make_async
def fetch_power_state(context: Session, place: Optional[PlaceName]) -> Union[PowerState, LabbyError]:
    return {
        ex: {
            place_name: {'power_state': True}
            for place_name, _ in place_data.items()
            if place is None or place_name == place
        }
        for exporter in places
        for ex, place_data in exporter.items()
    }


def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


def mock_labby(func_names: List[str]):
    for rpc_func in func_names:
        assert rpc.__dict__[rpc_func]
        assert callable(rpc.__dict__[rpc_func])
        assert sys.modules[__name__].__dict__[rpc_func]
        assert callable(sys.modules[__name__].__dict__[rpc_func])
        rpc.__dict__[rpc_func] = sys.modules[__name__].__dict__[rpc_func]

    def decorator(f):
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapped
    return decorator


class MockApplication(mock.MagicMock):
    pass


class MockSession(Session):
    pass


class Test(unittest.TestCase):

    @mock_labby(["fetch_places", "fetch_power_state"])
    @async_test
    async def test_places(self):
        context = MockSession()
        #############
        ret = await rpc.places(context)
        assert ret
        ret = await rpc.places(context, 'place1')
        assert ret

    @mock_labby(["fetch_places", "fetch_power_state"])
    @async_test
    async def test_power_states(self):
        context = MockSession()
        #############
        ret = await rpc.power_state(context, 'exporter', 'place1')
        assert ret
        assert ret['power_state']


if __name__ == "__main__":
    unittest.main()
