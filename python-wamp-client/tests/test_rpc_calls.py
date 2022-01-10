"""
Test all available remote procedure calls
"""
import asyncio
from time import sleep
import unittest
from random import choice
import subprocess
import os

from autobahn.asyncio.wamp import ApplicationRunner, ApplicationSession

class Component(ApplicationSession):
    """
    Application component that calls procedures which
    produce complex results and showing how to access those.
    """

    def onConnect(self):
        self.log.info(f"Connected to Coordinator, joining realm '{self.config.realm}'")
        self.join(self.config.realm)

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

        print("Polling places from router")
        places = await self.call(u"localhost.places")
        print(f"Received places: {places}")

        print("Polling power state for place")
        power_state = await self.call(u"localhost.power_state", choice(places)["name"])
        print(f"Received places: {power_state}")

        print("Polling specific place")
        res = await self.call(u"localhost.places", choice(places)["name"])
        print(f"Received places: {res}")

        place = choice(places)['name']
        print(f"Polling resource from {place}")
        res = await self.call(u'localhost.resource', place)
        print(f"Received resources: {res}")

        # place = choice(places)
        # group = place['matches'][0]['group']
        # resource = choice(list(res.items()))

        # print(f"Acquiring place {place}")
        # res = await self.call(u"localhost.acquire", place['name'], resource[0] , group)
        # print(f"Received: {res}")

        # print(f"Releasing place {place}")
        # res = await self.call(u"localhost.release", place['name'], resource[0] , group)
        # print(f"Received: {res}")

        print("Polling ALL resource")
        res = await self.call(u'localhost.resource')
        print(f"Received resources: {res}")

        temp = list(choice(list(res.values())).keys())
        name = choice(list(temp))
        print(f"Polling resource by name {name}")
        res = await self.call('localhost.resource_by_name', name)
        print(f"Received resources: {res}")

        place = choice(list(res))['place']
        print(f"Polling resource overview by place {place}")
        res = await self.call('localhost.resource_overview', place)
        print(f"Received resources: {res}")

        self.leave()


    def onDisconnect(self):
        asyncio.get_event_loop().stop()

class TestRpcCalls(unittest.TestCase):

    # def setUp(self) -> None:
        # os.chdir("../")
        # try:
        #     os.system("python run.py")
        #     self.process = None#subprocess.Popen(["python", "run.py"])
        #     sleep(6)
        #     pass
        # except Exception as exc:
        #     raise exc

    def test_rpc_calls(self) -> None:
        url = "ws://localhost:8083/ws"
        realm = "frontend"
        runner = ApplicationRunner(url, realm)
        try:
            runner.run(Component)
        except Exception as error:
            raise error

    # def tearDown(self) -> None:
    #     self.process.terminate()
    #     self.process.wait()
    #     pass

if __name__ == '__main__':
    # unittest.main()
    TestRpcCalls.test_rpc_calls(None)
