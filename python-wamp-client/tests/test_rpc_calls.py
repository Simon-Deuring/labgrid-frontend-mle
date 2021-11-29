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

    def onConnect(self):
        self.log.info(
            f"Connected to Coordinator, joining realm '{self.config.realm}'")
        self.join(self.config.realm, ['ticket'], "public")

    def onChallenge(self, challenge):
        self.log.info("Authencticating.")
        # authid = "public"
        if challenge.method == 'ticket':
            # TODO (Kevin) read user from config
            return ""
        else:
            # TODO (Kevin) handle other authentication methods
            self.log.error(
                "Only Ticket authentication enabled, atm. Aborting...")
            raise NotImplementedError(
                "Only Ticket authentication enabled, atm")

    async def onJoin(self, details):
        print("Polling places from router")
        res = await self.call('localhost.places')
        print(f"Received places: {res}")
        place = res[0]
        print(f"Polling resource from {place}")
        res = await self.call('localhost.resource', place)
        print(f"Received resources: {res}")
        print(f"Polling ALL resource")
        res = await self.call('localhost.resource')
        print(f"Received resources: {res}")
        self.leave()


    def onDisconnect(self):
        asyncio.get_event_loop().stop()


if __name__ == '__main__':
    url = "ws://127.0.0.1:20408/ws"
    realm = "realm1"
    runner = ApplicationRunner(url, realm)
    runner.run(Component)
