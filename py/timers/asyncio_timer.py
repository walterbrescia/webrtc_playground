import asyncio


class Timer:
    """
        Creates a timer with AsyncIO.create_task.
        __init__ requires the timeout (in seconds) and the callback function.
    """
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback

    def start(self):
        self._task = asyncio.create_task(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()
        await self._job()

    def cancel(self):
        self._task.cancel()


async def ping_callback():
    await asyncio.sleep(1)
    print('ping...')
    await ping_callback()

async def pong_callback():
    # await asyncio.sleep(0.1)
    print('pong!')


async def main():
    # ping_timer = Timer(1, ping_callback)  # set timer for two seconds
    pong_timer = Timer(0.75, pong_callback)  # set timer for two seconds

    print("Starting timers")
    # ping_timer.start()
    asyncio.create_task(ping_callback())
    pong_timer.start()
    # await asyncio.sleep(10.)  # wait to see timer works
    while True:
        await asyncio.sleep(0.001)

    # print('\nsecond example:')
    # timer = Timer(2, timeout_callback)  # set timer for two seconds
    # await asyncio.sleep(1)
    # ping_timer.cancel()  # cancel it
    pong_timer.cancel()  # cancel it
    # await asyncio.sleep(1.5)  # and wait to see it won't call callback
    


if __name__ == '__main__':

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
