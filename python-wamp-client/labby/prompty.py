import asyncio
import contextlib
import sys
from labby.labby import frontend_sessions, run_router


async def ainput(string: str) -> str:
    await asyncio.get_event_loop().run_in_executor(
        None, lambda s=string: sys.stdout.write(f'{s} '))

    return await asyncio.get_event_loop().run_in_executor(
        None, sys.stdin.readline)


def _parse(command: str):
    cmd_list = command.replace('\\n', '\n').strip().split(' ')
    cmd_list[0] = f"localhost.{cmd_list[0]}"
    for i, s in enumerate(cmd_list):
        if '=' in s:
            a, b = s.split('=')
            cmd_list[i] = {a.strip(): b.strip()}
    return cmd_list


async def prompty():
    count = 0
    while True:
        while len(frontend_sessions) == 0:
            print(f'Waiting for labby... {count}', end='\r')
            count += 1
            await asyncio.sleep(delay=1)
        command = await ainput('command: ')
        callback = frontend_sessions[0]
        try:
            if command and callback is not None:
                ret = await callback.call(*_parse(command))
                print(f"got>\n {ret}\n")
        except:
            pass


def run(backend_url, backend_realm, frontend_url, frontend_realm, keyfile_path, remote_url):
    with contextlib.suppress(KeyboardInterrupt):
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(prompty(), loop)
        run_router(backend_url, backend_realm,
                   frontend_url, frontend_realm, keyfile_path, remote_url)
