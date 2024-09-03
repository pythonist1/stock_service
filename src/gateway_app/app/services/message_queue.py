import asyncio
import aio_pika

from abstractions import AbstractService


class MessageConsumerService(AbstractService):
    def __init__(self, url: str, queue_name: str):
        super().__init__()
        self._url = url
        self._queue_name = queue_name

    async def start(self, loop):
        self._connection = await aio_pika.connect_robust(
            self._url
        )
        channel = await self._connection.channel()
        queue = await channel.declare_queue(self._queue_name, auto_delete=True)
        await channel.set_qos(prefetch_count=100)
        await queue.consume(self._process_callback)

    async def stop(self):
        await self._connection.close()
