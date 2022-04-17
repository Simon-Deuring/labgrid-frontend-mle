import asyncio
import contextlib
from pprint import pprint
import sys
import shlex
# from labby.labby import frontend_sessions, run_router

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

session = None


class Component(ApplicationSession):
    """
    An application component that subscribes and receives events.
    After receiving 5 events, it unsubscribes, sleeps and then
    resubscribes for another run. Then it stops.
    """

    def __init__(self, config=None):
        super().__init__(config)
        globals()["session"] = self

    async def onJoin(self, details):
        await self.subscribe(lambda x: print(f"onResourceChanged got: {x}"), "localhost.onResourceChanged")
        await self.subscribe(lambda x: print(f"onPlaceChanged    got: {x}"), "localhost.onPlaceChanged")

    def onDisconnect(self):
        asyncio.get_event_loop().stop()


async def ainput(string: str) -> str:
    await asyncio.get_event_loop().run_in_executor(
        None, lambda s=string: sys.stdout.write(f'{s} '))

    return await asyncio.get_event_loop().run_in_executor(
        None, sys.stdin.readline)


def _parse(command: str):
    cmd_list = shlex.split(command.strip())
    cmd_list[0] = f"localhost.{cmd_list[0]}"
    for i, s in enumerate(cmd_list):
        if '=' in s:
            a, b = s.split('=')
            cmd_list[i] = {a.strip(): b.strip()}
        if '.!' in s:
            cmd_list[i] = cmd_list[i].replace('.!', chr(28))
    return cmd_list


async def prompty():
    count = 0
    while True:
        while session is None:
            print(f'Waiting for labby... {count}', end='\r')
            count += 1
            await asyncio.sleep(delay=1)
        command = await ainput('command: ')
        callback = session
        try:
            if command and callback is not None:
                ret = await callback.call(*_parse(command))
                pprint(ret)
        except:
            pass


def run(backend_url, backend_realm, frontend_url, frontend_realm, keyfile_path, remote_url):
    with contextlib.suppress(KeyboardInterrupt):
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(prompty(), loop)
        # run_router(backend_url, backend_realm,
        #            frontend_url, frontend_realm, keyfile_path, remote_url)
        url = "ws://localhost:8083/ws"
        realm = "frontend"


def main():
    with contextlib.suppress(KeyboardInterrupt):
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(prompty(), loop)
        url = "ws://localhost:8083/ws"
        realm = "frontend"
        runner = ApplicationRunner(url, realm)
        coro = runner.run(Component)


if __name__ == "__main__":
    main()
