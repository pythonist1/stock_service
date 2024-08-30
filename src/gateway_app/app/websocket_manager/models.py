from collections import defaultdict

import attr
from fastapi import WebSocket

from .exceptions import WebsocketConnectionException


@attr.s(auto_attribs=True, frozen=True, hash=False, eq=False)
class WebsocketConnection:
    websocket: WebSocket
    user_id: str
    device_id: str

    def __eq__(self, other: 'WebsocketConnection') -> bool:
        return self.device_id == other.device_id

    def __hash__(self) -> int:
        return hash(self.device_id)


class ConnectionsPool:
    def __init__(self):
        self._connections = defaultdict(set)

    def add_connection(self,
                       websocket: WebSocket,
                       user_id: str,
                       device_id: str):
        connection = WebsocketConnection(
            websocket=websocket,
            user_id=user_id,
            device_id=device_id,
        )
        self._connections[user_id].discard(connection)
        self._connections[user_id].add(connection)

    def _get_connection(self, user_id: str, device_id: str):
        device_connection = next(
            (connection for connection in self._connections.get(user_id, ()) if connection.device_id == device_id),
            None
        )
        if not device_connection:
            raise WebsocketConnectionException('Websocket connection not found in cache')
        return device_connection

    def get_connection(self, user_id: str, device_id: str):
        connection = self._get_connection(user_id=user_id, device_id=device_id)
        return connection

    def get_user_websockets(self, user_id: str):
        websockets = tuple(connection.websocket for connection in self._connections.get(user_id, ()))
        if not websockets:
            raise WebsocketConnectionException('Websocket connection not found in cache')
        return websockets

    def get_websockets_by_users(self, users_ids: list):
        websockets = list()
        for user_id in users_ids:
            if user_connections := self._connections.get(user_id, None):
                for connection in user_connections:
                    websockets.append(connection.websocket)
        return websockets

    def get_all_websockets(self):
        websockets = list()
        for user_connections in self._connections.values():
            websockets.extend(user_connections)
        return websockets

    def remove_connection(self,
                          user_id: str,
                          device_id: str):
        connection = self._get_connection(user_id, device_id)
        self._connections[user_id].remove(connection)
        if not self._connections[user_id]:
            del self._connections[user_id]
