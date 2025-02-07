import asyncio
import socketio
import ssl
import threading
import time

ALIVE_TIMER = 1
ALIVE = 1
DEAD = 0
DISCONNECTED = -1
STATUS = DEAD

sio = socketio.AsyncClient(ssl_verify=False)
sid = sio.get_sid()

@sio.event
async def connect():
    global STATUS
    print('connection established')
    STATUS = ALIVE
    print("setting STATUS: ", STATUS)
    

@sio.event
async def disconnect():
    global STATUS
    print('disconnected from server')
    STATUS = DISCONNECTED

@sio.event
async def peers(data):
    print('peers:', data)

async def main():
    # timer = Timer(ALIVE_TIMER, alive_cb)
    asyncio.ensure_future(alive_cb())
    await sio.connect('https://0.0.0.0:443/')
    await sio.wait()

async def alive():
    global STATUS
    print("STATUS: ", STATUS)
    if STATUS == ALIVE:
        await sio.emit('available', {"ID": "Turtlebot3"})

async def alive_cb():
    global STATUS
    # print(" alive_cb")
    # while True:
    await asyncio.sleep(ALIVE_TIMER)
    if STATUS != DISCONNECTED:
        await alive()
            # time.sleep(ALIVE_TIMER)
    await alive_cb()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected, closing event loop.")
        # asyncio.run(sio.disconnect())