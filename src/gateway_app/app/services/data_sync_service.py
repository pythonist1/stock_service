import asyncio
from abstractions import AbstractService


class DataSyncService(AbstractService):
    def __init__(self):
        self._stop_event = False

    async def start(self, loop):
        self._start_callback()
        self._task = asyncio.create_task(self.read_in_loop())

    async def stop(self):
        self._task.cancel()
        self._stop_event = True

    async def read_in_loop(self):
        while not self._stop_event:
            await self._process_callback()
            await asyncio.sleep(15)
