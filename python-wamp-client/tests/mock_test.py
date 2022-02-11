import asyncio
import sys
from typing import Callable
import unittest
from unittest import mock

from labby.labby_types import Session

sys.path.append(".")
sys.path.append("labby")

from labby import rpc

def make_async(f: Callable):
    def wrapper(*args, **kwargs):
        future = asyncio.Future()
        future.set_result(f(*args, **kwargs))
        return future
    return wrapper 


@make_async
def fetch_places(*args, **kwarfs):
    return {"cup": {"place1": {}}}


@make_async
def fetch_power_state(*args, **kwargs):
    return {"cup":{"place1":True}}


rpc.fetch_places = fetch_places
rpc.fetch_power_state = fetch_power_state

def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper

class MockApplication(mock.MagicMock):
    pass

class MockSession(Session):
    pass
    

class Test(unittest.TestCase):

    @async_test
    async def test_places(self):
        context = MockSession()
        ret = await rpc.places(context)


if __name__ == "__main__":

    unittest.main()
