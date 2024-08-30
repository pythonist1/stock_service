from typing import Collection

from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from websockets.exceptions import ConnectionClosedOK

from .models import ConnectionsPool, WebsocketConnection
from .exceptions import WebsocketConnectionException


class WebsocketManager:
    def __init__(self):
        self._connections_pool = ConnectionsPool()
        self.handle_client_message = None

    async def connect(self,
                      websocket: WebSocket,
                      user_id: str,
                      device_id: str):
        await websocket.accept()
        self._connections_pool.add_connection(
            *(websocket, user_id, device_id)
        )

    def disconnect(self, user_id: str, device_id: str):
        self._connections_pool.remove_connection(
            user_id=user_id,
            device_id=device_id
        )

    def clear_connection_cache(self, user_id: str, device_id: str):
        try:
            self._connections_pool.remove_connection(
                user_id=user_id,
                device_id=device_id
            )
        except WebsocketConnectionException:
            pass

    async def send_message_to_user(self, data: dict, user_id: str):
        websockets: Collection[WebSocket] = self._connections_pool.get_user_websockets(user_id)
        for websocket in websockets:
                await websocket.send_json(data)

    async def send_message_to_user_device(self, data: dict, user_id: str, device_id: str):
        connection = self._connections_pool.get_connection(
            user_id=user_id,
            device_id=device_id
        )
        await connection.websocket.send_json(data)

    async def send_message_to_users(self, data: dict, user_ids: list):
        websockets: Collection[WebSocket] = self._connections_pool.get_websockets_by_users(user_ids)

        for websocket in websockets:
            if websocket.client_state is WebSocketState.CONNECTED:
                try:
                    await websocket.send_json(data)
                except ConnectionClosedOK:
                    pass

    async def broadcast(self, data: dict):
        websockets: Collection[WebsocketConnection] = self._connections_pool.get_all_websockets()

        # print(data)
        for ws_connection in websockets:
            await ws_connection.websocket.send_json(data)
