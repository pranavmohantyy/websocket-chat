from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from collections import defaultdict

app = FastAPI()

rooms = defaultdict(list)

class ConnectionManager:
    def __init__(self):
        self.active_connections = defaultdict(list)
        self.message_history = defaultdict(list)

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[room_id].append(websocket)
        self.broadcast(room_id, f"{websocket.client} joined")
        await self.send_history(room_id, websocket)

    async def disconnect(self, room_id: str, websocket: WebSocket):
        self.active_connections[room_id].remove(websocket)
        self.broadcast(room_id, f"{websocket.client} left")

    def broadcast(self, room_id: str, message: str):
        for connection in self.active_connections[room_id]:
            asyncio.create_task(connection.send_text(message))

    async def send_history(self, room_id: str, websocket: WebSocket):
        if room_id in self.message_history:
            for message in self.message_history[room_id]:
                await websocket.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("/dm "):
                parts = data.split(' ', 2)
                if len(parts) == 3:
                    username = parts[1]
                    message = parts[2]
                    await manager.send_private_message(room_id, username, message)
                continue
            manager.message_history[room_id].append(data)
            manager.broadcast(room_id, data)
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)

async def send_private_message(room_id: str, username: str, message: str):
    for connection in manager.active_connections[room_id]:
        if connection.client.host == username:
            await connection.send_text(f"[DM] {message}")

@app.get("/")
def get():
    return HTMLResponse(content="<html><body><h1>WebSocket Chat</h1></body></html>")