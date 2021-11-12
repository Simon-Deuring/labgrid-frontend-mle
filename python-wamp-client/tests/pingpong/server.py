#!/bin/env python3
import asyncio
from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory

class ServerProtocol(WebSocketServerProtocol):
    """
    ServerProtocol -
        Communictaion layer between coordinator and client
        offers
    """
    def onConnect(self, request):
        # TODO remove example code
        print("Client connecting: {}".format(request.peer))

    def onOpen(self):
        # TODO remove example code
        print("Connection now open")

    def onMessage(self, payload, is_binary):
        # TODO remove example code
        if is_binary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))
        # echo back message verbatim
        self.sendMessage(payload, is_binary)

    def onClose(self, was_clean, code, reason):
        # TODO remove example code
        print("WebSocket connection closed: {0}".format(reason))

def run_server(domain: str = 'localhost', port: int = 4201, listen_addr: str = '0.0.0.0'):
    """
    runs a new server instance on domain:port and listens to connections from listen_addr
    blocking
    """
    loop = asyncio.get_event_loop()
    factory = WebSocketServerFactory("ws://{domain}:{port}/".format(domain=domain, port=port))
    factory.protocol = ServerProtocol

    server_coroutine = loop.create_server(factory, listen_addr, port)
    server = loop.run_until_complete(server_coroutine)

    try:
        loop.run_forever()
    except KeyboardInterrupt as err:
        print("Shutting down Server...", err)
    finally:
        server.close()
        loop.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # TODO(Kevin) parse args
        domain = sys.argv[1]
        run_server(domain)
    else:
        run_server()
