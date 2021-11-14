"""
Test all available remote procedure calls
"""
#TODO(Kevin) convert into unit test, requires launcher/launchoptions for router and must start RPC provider


import asyncio
from os import environ
from autobahn.wamp.types import CallResult
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner


class Component(ApplicationSession):
    """
    Application component that calls procedures which
    produce complex results and showing how to access those.
    """

    async def onJoin(self, details):
        print("Polling places from router")
        res = await self.call('localhost.places')
        print(f"Received places: {res}")
        print(f"Polling resource from {res['places'][1]}")
        res = await self.call('localhost.resource', res['places'][1])
        print(f"Received resources: {res}")
        print(f"Polling ALL resource")
        res = await self.call('localhost.resource')
        print(f"Received resources: {res}")
        self.leave()

    def onDisconnect(self):
        asyncio.get_event_loop().stop()


if __name__ == '__main__':
    url = "ws://127.0.0.1:8080/ws"
    realm = "crossbardemo"
    runner = ApplicationRunner(url, realm)
    runner.run(Component)
