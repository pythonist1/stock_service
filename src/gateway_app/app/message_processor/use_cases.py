import json
import aio_pika
from websocket_manager import WebsocketManager
from abstractions import AbstractWorkerManager, AbstractActualDataManager


class MessageUseCases:
    def __init__(self,
                 websocket_manager: WebsocketManager,
                 worker_manager: AbstractWorkerManager,
                 actual_data_manager: AbstractActualDataManager):
        self._websocket_manager = websocket_manager
        self._worker_manager = worker_manager
        self._actual_data_manager = actual_data_manager
        self._websocket_manager.handle_client_message = self.handle_client_message

    async def send_message_to_client(self, message: aio_pika.abc.AbstractIncomingMessage):
        async with message.process():
            message_data = json.loads(message.body)
            if message_data.get("user_id"):
                if message_data.get("aggregation_result"):
                    await self._websocket_manager.send_message_to_user(message_data, message_data["user_id"])

    async def handle_client_message(self, message: dict):
        print("message", message)
        user_data = json.loads(message.get("text", "{}"))
        if user_data.get("action") == "aggregate_data":
            self._worker_manager.aggregate_data(user_data["aggregation_params"])

    async def sync_data(self):
        data = await self._actual_data_manager.get_actual_data()
        await self._websocket_manager.broadcast(data)
        await self._websocket_manager.broadcast(self._actual_data_manager.get_demonstration_data())

    def collect_stocks(self):
        self._worker_manager.collect_stocks()

    async def stop_adapters(self):
        await self._actual_data_manager.stop()
