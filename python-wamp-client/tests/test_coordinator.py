###############################################################################
##
# Copyright (C) Tavendo GmbH and/or collaborators. All rights reserved.
##
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
##
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
##
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
##
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
##
###############################################################################

from autobahn.asyncio.wamp import ApplicationSession
from ..labby import rpc

TICKETS = {
    'user1': '123secret',
    'user2': '456secret'
}

class ClientSession(ApplicationSession):

    def onConnect(self):
        realm = self.config.realm
        authid = self.config.extra['authid']
        print("ClientSession connected. Joining realm <{}> under authid <{}>".format(
            realm if realm else 'not provided', authid))
        self.join(realm, ['ticket'], authid)

    def onChallenge(self, challenge):
        print("ClientSession challenge received: {}".format(challenge))
        if challenge.method == 'ticket':
            authid = self.config.extra['authid']
            return ""
        else:
            raise Exception("Invalid authmethod {}".format(challenge.method))

    async def onJoin(self, details):
        print("ClientSession joined: {}".format(details))
        self.subscribe("mle-lg-ref-1")
        res = await rpc.places(self)
        print("PLACES")
        print(list(res), "\n")
        res = await rpc.resource(self, 'cup', 'mle-lg-ref-1')
        print("RESOURCES")
        print(res)
        self.leave()

    def onLeave(self, details):
        print("ClientSession left: {}".format(details))
        self.disconnect()

    def onDisconnect(self):
        print("ClientSession disconnected")


if __name__ == '__main__':

    import sys

    url = u"ws://localhost:20408/ws"
    realm = "realm1"
    authid = "public"

    from autobahn.asyncio.wamp import ApplicationRunner

    extra = {
        'authid': authid
    }
    print("Connecting to {}: realm={}, authid={}".format(url, realm, authid))

    runner = ApplicationRunner(url=url, realm=realm, extra=extra)
    runner.run(ClientSession)
