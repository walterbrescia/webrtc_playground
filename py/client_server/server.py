import argparse
import asyncio
import json
import logging
import uuid
import yaml

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription

logger = logging.getLogger("pc")
pcs = set()

async def offer(request):
    try:
        params = await request.json()
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
        pc = RTCPeerConnection()
        pc_id = f"PeerConnection({uuid.uuid4()})"
        pcs.add(pc)

        def log_info(msg, *args):
            logger.info(pc_id + " " + msg, *args)

        log_info("Created for %s", request.remote)

        @pc.on("datachannel")
        def on_datachannel(channel):
            @channel.on("message")
            def on_message(message):
                message = json.loads(message)
                # log_info("Message header: ", message['header'])
                log_info("Message data: %s", message['data'])
                # if isinstance(message, str) and message.startswith("ping"):
                #     channel.send("pong" + message)

        @pc.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            log_info("ICE connection state: %s", pc.iceConnectionState)
            if pc.iceConnectionState == "failed":
                await pc.close()
                pcs.discard(pc)

        # Handle offer and create answer
        await pc.setRemoteDescription(offer)
        log_info("Set remote description")

        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        log_info("Created and set local description")

        return web.Response(
            content_type="application/json",
            text=json.dumps(
                {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
            ),
        )
    except Exception as e:
        logger.error(f"Error in offer handling: {str(e)}")
        return web.Response(status=500, text="Internal Server Error")

async def on_shutdown(app):
    # Close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebRTC audio/video/data-channels demo")
    parser.add_argument("--port", type=int, default=8080, help="Port for HTTP server (default: 8080)")
    # parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()

    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_post("/", offer)
    web.run_app(app, access_log=None, port=args.port)
