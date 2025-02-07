import asyncio
import json
import logging
from aiohttp import ClientSession
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer

SIGNALING_SERVER_URL = "http://0.0.0.0:8080/offer"  # URL of the server

logger = logging.getLogger("pc")

RUNNING = 1
STOPPED = 0
STATE = RUNNING

async def send_offer(pc):
    # Create offer
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    # Send offer to the signaling server
    async with ClientSession() as session:
        async with session.post(SIGNALING_SERVER_URL, json={
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }) as response:
            data = await response.json()
            print("Received answer:", data)

    # Set remote description
    answer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
    await pc.setRemoteDescription(answer)
    print("Set remote description")

async def run(pc):

    # Create data channel
    channel = pc.createDataChannel("chat")

    # Wait for the data channel to open before sending messages
    @channel.on("open")
    async def on_open():
        print("Data channel is open")
        while STATE == RUNNING and pc.iceConnectionState == "completed":
            data = '{"header": "this is the header", "data": "this is the data"}'
            channel.send(data)
            print("Sent:", data)
            await asyncio.sleep(1)

    @channel.on("close")
    def on_close():
        STATE = STOPPED
        print("Data channel is closed.")
        # close the connection
        # asyncio.create_task(cleanup(pc))

    # Log ICE candidates as they are added
    @pc.on("icecandidate")
    async def on_icecandidate(candidate):
        if candidate:
            print("New ICE candidate:", candidate)

    # Log connection state changes
    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        print("ICE connection state:", pc.iceConnectionState)
        if pc.iceConnectionState == "failed":
            print("ICE connection failed, closing peer connection")
            await pc.close()
        elif pc.iceConnectionState == "connected":
            print("ICE connection established!")
        elif pc.iceConnectionState == "closed":
            exit()

    # Send the offer to the signaling server
    await send_offer(pc)

if __name__ == "__main__":

    # Configure peer connection with a STUN server
    ice_server = RTCIceServer("stun:stun.l.google.com:19302")
    # configuration = RTCConfiguration(iceServers=[ice_server])
    configuration = RTCConfiguration(iceServers=[])
    pc = RTCPeerConnection(configuration=configuration)

    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(pc))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected, closing event loop.")
        loop.run_until_complete(pc.close())
    # finally:
    #     loop.close()
