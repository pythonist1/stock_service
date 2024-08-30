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
        self._channel = await self._connection.channel()
        self._queue = await self._channel.declare_queue(self._queue_name, auto_delete=True)
        await self._channel.set_qos(prefetch_count=100)
        loop.create_task(self._queue.consume(self._process_callback))
        await loop.create_future()

    async def stop(self):
        await self._connection.close()
