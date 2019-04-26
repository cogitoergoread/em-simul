import asyncio
from contextlib import suppress
import websockets


async def start():
    # your infinite loop here, for example:
    while True:
        print('Start Loop')
        async with websockets.connect(
                'wss://ah1.connectmedia.hu/app?token=vgEAhQAAABNhaDEuY29ubmVjdG1lZGlhLmh13GsVZpRi0N-ZlAwihv3VwQ==') as websocket:
            greeting = websocket.recv()
            print(f"< {greeting}")
            await asyncio.sleep(1)
        print('Asy után')


async def main():
    task = asyncio.Task(start())

    # let script some time to work:
    await asyncio.sleep(3)

    # cancel task to avoid warning:
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task  # await for task cancellation


if __name__ == '__main__':
    print('Start')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        print('Try')
        loop.run_until_complete(main())
        print('Try veg')
    finally:
        print('Final')
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        print('Final veg')
