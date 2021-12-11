"""
Test all available remote procedure calls
"""
# TODO(Kevin) convert into unit test, requires launcher/launchoptions for router and must start RPC provider

import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from random import choice
class Component(ApplicationSession):
    """
    Application component that calls procedures which
    produce complex results and showing how to access those.
    """

    def onConnect(self):
        self.log.info(
            f"Connected to Coordinator, joining realm '{self.config.realm}'")
        self.join(self.config.realm)

    async def onJoin(self, details):
        res = await self.call(u"wamp.registration.list")
        print(res)
        procs = []
        for proc in res['exact']:
            p = await self.call(u"wamp.registration.get", proc)
            print(p)
            procs.append(p)

        print("Polling places from router")
        res = await self.call(u"localhost.places")
        print(f"Received places: {res}")

        print("Polling specific place")
        res = await self.call(u"localhost.places", choice(res)["name"])
        print(f"Received places: {res}")

        place = res[0]['name']
        print(f"Polling resource from {place}")
        res = await self.call(u'localhost.resource', place)
        print(f"Received resources: {res}")

        print("Polling ALL resource")
        res = await self.call(u'localhost.resource')
        print(f"Received resources: {res}")
        self.leave()

    def onDisconnect(self):
        asyncio.get_event_loop().stop()


if __name__ == '__main__':
    url = "ws://localhost:8083/ws"
    realm = "frontend"
    runner = ApplicationRunner(url, realm)
    runner.run(Component)
