import asyncio
from typing import List
from abstractions import AbstractService

class Entrypoint:
    def __init__(self, servisec: List[AbstractService]):
        self._servisec = servisec
        self._loop = asyncio.new_event_loop()

    def __enter__(self):
        self._loop.run_until_complete(self.__aenter__())
        self._loop.create_future()
        return self._loop

    async def __aenter__(self):
        await asyncio.gather(*[self._start_service(svc) for svc in self._servisec])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._loop.is_closed():
            return

        self._loop.run_until_complete(self.__aexit__(exc_type, exc_val, exc_tb))
        self._loop.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for svc in self._servisec:
            await svc.stop()

    async def _start_service(self, service):
        await service.start(self._loop)

