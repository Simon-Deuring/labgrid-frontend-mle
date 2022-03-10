"""
Test all available remote procedure calls
"""
from typing import Optional

import asyncio
from time import sleep
import unittest
from random import choice
from autobahn.asyncio.wamp import ApplicationRunner, ApplicationSession

CLIENT_REF : ApplicationSession = None

class Client(ApplicationSession):
    """
    Application component that calls procedures which
    produce complex results and showing how to access those.
    """

    def __init__(self, config=None):
        global CLIENT_REF
        CLIENT_REF = self
        super().__init__(config=config)


    def onConnect(self):
        self.join(self.config.realm)

    
    def onLeave(self, details):
        self.log.info("Session disconnected.")
        self.disconnect()


    async def onJoin(self, details):
        # info = await self.call("localhost.info", "places")
        # print(info)
        # info = await self.call("localhost.info")
        # print(info)
        # res = await self.call(u"wamp.registration.list")
        # print(res)
        # procs = []
        # for proc in res['exact']:
        #     p = await self.call(u"wamp.registration.get", proc)
        #     print(p)
        #     procs.append(p)

        # print("Polling places from router")
        # places = await self.call(u"localhost.places")
        # print(f"Received places: {places}")

        # place_name = choice(places)['name']
        # print(f"Polling place {place_name}")
        # place_ = await self.call(u"localhost.places", place_name)
        # print(f"Received places: {place_}")

        # print("Polling power state for place")
        # place = choice(places)["name"]
        # power_state = await self.call(u"localhost.power_state", place)
        # print(f"Received power state for place {place}: {power_state}")

        # print("Polling specific place")
        # res = await self.call(u"localhost.places", choice(places)["name"])
        # print(f"Received places: {res}")

        # place = choice(places)['name']
        # print(f"Polling resource from {place}")
        # res = await self.call(u'localhost.resource', place)
        # print(f"Received resources: {res}")

        # place = choice(places)
        # group = place['matches'][0]['group']
        # resource = choice(list(res.items()))

        # print(f"Acquiring place {place}")
        # res = await self.call(u"localhost.acquire", place['name'])
        # res = await self.call(u"localhost.acquire", "mle-lg-ref-1")
        # print(f"Received: {res}")

        # print(f"Releasing place {place}")
        # res = await self.call(u"localhost.release", place['name'])
        # print(f"Received: {res}")

        # print("Polling ALL resource")
        # res = await self.call(u'localhost.resource')
        # print(f"Received resources: {res}")

        # temp = list(choice(list(res.values())).keys())
        # name = choice(list(temp))
        # print(f"Polling resource by name {name}")
        # res = await self.call('localhost.resource_by_name', name)
        # print(f"Received resources: {res}")

        # place = choice(list(res))['place']
        # print(f"Polling resource overview by place {place}")
        # res = await self.call('localhost.resource_overview', place)
        # print(f"Received resources: {res}")

        # self.leave()
        pass


def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper

class TestRpcCalls(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        try:

            sleep(6)

            url = "ws://localhost:8083/ws"
            realm = "frontend"
            runner = ApplicationRunner(url=url, realm=realm, extra=None)
            coro = runner.run(Client, start_loop=False)
            loop = asyncio.get_event_loop()
            assert coro
            assert loop
            loop.run_until_complete(coro)
            global CLIENT_REF
            cls.client = CLIENT_REF
        except Exception as exc:
            raise exc from exc

    @async_test
    def test_call_places_all(self):
        client = self.client
        res = yield from client.call("localhost.places")
        print(res)

    @async_test
    def test_call_acquire_release(self):
        client = self.client
        client.call("localhost.reservations")
        res = yield from client.call("localhost.acquire", "place1")
        print(res)
        res = yield from client.call("localhost.release", "place1")
        print(res)

    @async_test
    async def test_forward(self):
        client = self.client
        res = await client.call("forward", "get_places")
        print(res)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.client:
            cls.client.leave()




if __name__ == '__main__':

    import subprocess
    process = subprocess.Popen(["python", "-m", "labby",
                        "--backend_url", "ws://localhost:20408/ws",
                        "--backend_realm", "realm1",
                        "--frontend_url", "ws://localhost:8083/ws",
                        "--frontend_realm", "frontend",
                        "--exporter", "cup"
                    ])

    unittest.main()

    if process:
        process.terminate()
        process.wait()
        assert process.returncode

