#!/usr/bin/env python
# WS server that sends messages at random intervals
import asyncio
import datetime
import random
import websockets


async def time(websocket, path):
    print('Start... Loop előtt')
    while True:
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        print(now)
        await websocket.send(now)
        await asyncio.sleep(random.random() * 3)


if __name__ == '__main__':
    print('Server is starting')
    start_server = websockets.serve(time, 'localhost', 5678)
    asyncio.get_event_loop().run_until_complete(start_server)
    print('Server started')
    asyncio.get_event_loop().run_forever()
    print('Forever vége')
