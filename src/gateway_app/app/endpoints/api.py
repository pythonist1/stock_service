import json
import traceback
from fastapi import APIRouter, WebSocket, Request, Depends

from authorization import AuthHandler
from websocket_manager import WebsocketManager

from .pydantic_schemas import User

router = APIRouter()


def get_ws_manager(websocket: WebSocket):
    ws_manager: WebsocketManager = websocket.app.state.websocket_manager
    return ws_manager

def get_auth_handler(request: Request):
    return request.app.state.auth_handler


@router.post("/authorize/")
async def get_user_id(user: User, auth_handler: AuthHandler = Depends(get_auth_handler)):
    user_id = await auth_handler.get_user_id(user.name)
    return {"user_id": user_id}


@router.websocket('/connect/websocket/{user_id}/{device_id}/')
async def websocket_endpoint(
        websocket: WebSocket,
        user_id: str,
        device_id: str,
        ws_manager = Depends(get_ws_manager)):

    try:
        await ws_manager.connect(websocket, user_id, device_id)
        while True:
            message = await websocket.receive()
            await ws_manager.handle_client_message(message)
    except Exception:
        exp_message = traceback.format_exc()
        print(exp_message)
    finally:
        ws_manager.clear_connection_cache(user_id, device_id)
