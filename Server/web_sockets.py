import asyncio
from dataclasses import dataclass
from typing import Callable
from typing import List

from fastapi import WebSocket


@dataclass
class WebSocketAndId:
    socket: WebSocket
    id: int


class ConnectionManager:
    is_blocking: bool = False

    def __init__(self):
        self.active_connections: List[WebSocketAndId] = []

    async def connect(self, websocket: WebSocket, socket_id: int):
        await websocket.accept()
        self.active_connections.append(WebSocketAndId(websocket, socket_id))

    def disconnect(self, websocket: WebSocket, socket_id: int):
        self.active_connections.remove(WebSocketAndId(websocket, socket_id))

    def unblock_clients(self):
        self.is_blocking = False
        self.broadcast("unblock")

    def block_clients(self):
        self.is_blocking = True
        self.broadcast("block")

    async def awaitable_block_clients(self):
        self.is_blocking = True
        for connection in self.active_connections:
            await connection.socket.send_text("block")

    # notice: changed from async to sync as background tasks mess up with async functions
    # https://stackoverflow.com/questions/73707373/how-to-return-the-result-of-backgroundtasks-as-websocket-answer-in-fastapi
    def send_text_to_client(
        self, client_id: int, message: str, on_no_client_found: Callable
    ):
        for socket_and_id in self.active_connections:
            if socket_and_id.id == client_id:
                #
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                loop.run_until_complete(socket_and_id.socket.send_text(message))
                return
        on_no_client_found(client_id, message)

    def broadcast(self, message: str):
        for connection in self.active_connections:
            self.send_text_to_client(connection.id, message, lambda x: None)
