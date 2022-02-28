import asyncio
import labby
from labby.labby import get_frontend_callback, run_router


async def prompty():
    count = 0
    while True:
        while labby.get_frontend_callback() is None:
            print(f'Waiting for labby... {count}', end='\r')
            count += 1
            await asyncio.sleep(delay=.5)
        command = input('command: ')
        callback = get_frontend_callback()
        try:
            if callback is not None:
                ret = await callback.call(*command.split(' '))
                print(f"got>\n {ret}\n")
        except:
            pass

def main():
    try:
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(prompty(), loop)
        run_router('ws://localhost:20408/ws', 'realm1')
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
