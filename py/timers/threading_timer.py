import threading

class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback

    def start(self):
        self._task = threading.Timer(self._timeout, self._job)
        self._task.start()

    def _job(self):
        self._callback()
        self.start()

    def cancel(self):
        self._task.cancel()


def ping_callback():
    print('ping...')
    # await asyncio.sleep(0.1)

def pong_callback():
    print('pong!')
    # await asyncio.sleep(0.1)


def main():
    ping_timer = Timer(1, ping_callback)  # set timer for two seconds
    pong_timer = Timer(0.75, pong_callback)  # set timer for two seconds

    print("Starting timers")
    ping_timer.start()
    pong_timer.start()
    # await asyncio.sleep(10.)  # wait to see timer works
    threading.Event().wait(10)
    print("Timeout")

    # print('\nsecond example:')
    # timer = Timer(2, timeout_callback)  # set timer for two seconds
    # await asyncio.sleep(1)
    ping_timer.cancel()  # cancel it
    pong_timer.cancel()  # cancel it
    # await asyncio.sleep(1.5)  # and wait to see it won't call callback

if __name__ == '__main__':
    main()