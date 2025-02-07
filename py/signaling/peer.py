import asyncio
import socketio
import ssl
import threading
import time

"""
    -------------------------------------------------------------------------------------------------------

    The following sys operations allow the import of custom timer classes
    from the custom "timers" module.
    In general, it should not be done and should be replaced with a proper package installation,
    i.e. pip install -e . or python setup.py install, where setup.py should be done.
"""
import sys
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append("/root/ws/py")
"""
    -------------------------------------------------------------------------------------------------------
"""

from timers import AsyncIOTimer, ThreadingTimer

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
    # await alive_cb()

async def get_peers():
    await sio.emit('get_peers')

@sio.event
async def reply_peers(data):
    print('Peers:')
    for peer in data:
        print("    * ", peer, data[peer])

async def main():
    # timer = Timer(ALIVE_TIMER, alive_cb)
    alive_timer = AsyncIOTimer(ALIVE_TIMER, alive_cb)
    alive_timer.start()
    peers_timer = AsyncIOTimer(ALIVE_TIMER, get_peers)
    peers_timer.start()
    # asyncio.ensure_future(alive_cb())
    await sio.connect('https://0.0.0.0:443')
    await sio.wait()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected, closing event loop.")
        # asyncio.run(sio.disconnect())