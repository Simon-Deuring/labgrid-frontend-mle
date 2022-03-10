import asyncio
import sys
import labby
from labby.labby import get_frontend_callback, run_router


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
        while labby.get_frontend_callback() is None:
            print(f'Waiting for labby... {count}', end='\r')
            count += 1
            await asyncio.sleep(delay=1)
        command = await ainput('command: ')
        callback = get_frontend_callback()
        try:
            if command and callback is not None:
                ret = await callback.call(*_parse(command))
                print(f"got>\n {ret}\n")
        except:
            pass


def run(backend_url, backend_realm, frontend_url, frontend_realm, exporter):
    try:
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(prompty(), loop)
        run_router(backend_url, backend_realm,
                   frontend_url, frontend_realm, exporter)
    except KeyboardInterrupt:
        pass
