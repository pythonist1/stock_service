import asyncio
from abstractions import AbstractService


class DataSyncService(AbstractService):
    async def start(self, loop):
        self._start_callback()
        while True:
            await self._process_callback()
            await asyncio.sleep(5)

    async def stop(self):
        pass
