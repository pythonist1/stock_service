import asyncio
from typing import List
from abstractions import AbstractService
from message_processor import MessageProcessor


class Entrypoint:
    def __init__(self, servisec: List[AbstractService], message_processor: MessageProcessor):
        self._servisec = servisec
        self._message_processor = message_processor
        self._loop = asyncio.new_event_loop()

    def __enter__(self):
        self._loop.run_until_complete(self.__aenter__())
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
        await self._message_processor.stop()
        for svc in self._servisec:
            await svc.stop()

    async def _start_service(self, service):
        await service.start(self._loop)
