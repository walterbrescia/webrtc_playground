from aiohttp import web
import socketio
import logging
import ssl
import json
import threading
import asyncio
import copy

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

app = web.Application()
sio = socketio.AsyncServer()
sio.attach(app)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

ALIVE = 1
DEAD = 0
CHECK_RATE = 1
TIME_TO_LIVE = 3
REMOVE_DEADS_TH = -1
CHECKS_TO_LIVE = TIME_TO_LIVE / CHECK_RATE

peers = {}

@sio.event
def connect(sid, environ):
    global peers
    print("New connection ", sid)
    # If the peer is already in the list, remove it.
    # This allows to update the peer's status and info.
    # peers_ = copy.deepcopy(peers)
    # for peer in peers_:
    #     if peers_[peer]["REMOTE_ADDR"] == environ["REMOTE_ADDR"] and peers_[peer]["REMOTE_PORT"] == environ["REMOTE_PORT"]:
    #         peers.pop(peer)
    peers[sid] = {
        "REMOTE_ADDR": environ['REMOTE_ADDR'], 
        "REMOTE_PORT": environ['REMOTE_PORT'], 
        "STATUS": ALIVE,
        "CHECKS_TO_LIVE": CHECKS_TO_LIVE
    }

@sio.event
async def disconnect(sid):
    print("Disconnecting ", sid)
    await drop_sid(sid)

@sio.event
async def available(sid, data):
    global peers
    """Serve the client-side application."""
    print("received ", sid, data)
    peers[sid]["STATUS"] = ALIVE
    peers[sid]["CHECKS_TO_LIVE"] = CHECKS_TO_LIVE
    peers[sid]["ID"] = data["ID"]

async def drop_sid(sid):
    global peers
    if sid in peers:
        peers.pop(sid)
        await sio.disconnect(sid)

async def check_peers():
    # print("Checking peers...")
    global peers
    dead_sids = []
    for sid in peers:
        peers[sid]['CHECKS_TO_LIVE'] -= 1
        if peers[sid]['CHECKS_TO_LIVE'] == 0:
            peers[sid]['STATUS'] = DEAD
            print("Peer ", peers[sid], " is dead.")
        if peers[sid]["CHECKS_TO_LIVE"] < REMOVE_DEADS_TH:
            dead_sids.append(sid)
    for sid in dead_sids:
        print("Disconnecting dead sid: ", sid)
        drop_sid(sid)
    
    print("Peers: ")
    for peer in peers:
        print("    * ", peer, peers[peer])
    # await broadcast_peers()
    # threading.Timer(CHECK_RATE, check_peers).start()
    # await asyncio.sleep(CHECK_RATE)
    # await check_peers()

@sio.event
async def get_peers(sid):
    global peers
    print(sid, " requested available peers.")
    peers_ = copy.deepcopy(peers)
    # peers_.pop(sid)
    await sio.emit('reply_peers', peers_, room=sid)

async def main():
    global web
    # asyncio.create_task(check_peers())
    check_peers_timer = AsyncIOTimer(CHECK_RATE, check_peers)
    # check_peers_timer = ThreadingTimer(CHECK_RATE, check_peers)
    check_peers_timer.start()
    print("starting server")
    # web.run_app(app, port=443, ssl_context=ssl_context)


if __name__ == '__main__':
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain('keys/cert.pem', 'keys/key.pem')
    # app.router.add_post('/available', available)
    # app.router.add_post('/get_peers', get_peers)
    try:
        loop.run_until_complete(main())
        web.run_app(app, port=443, ssl_context=ssl_context, loop=loop)
        while True:
            pass
        print("exiting")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
    