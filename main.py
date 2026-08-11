from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from collections import defaultdict
import time

app = FastAPI()

rooms = defaultdict(list)

class ConnectionManager:
    def __init__(self):
        self.active_connections = defaultdict(list)
        self.message_history = defaultdict(list)
        self.message_timestamps = defaultdict(lambda: defaultdict(float))

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[room_id].append(websocket)
        self.broadcast(room_id, f"{websocket.client} joined")
        await self.send_history(room_id, websocket)

    async def send_history(self, room_id: str, websocket: WebSocket):
        for message in self.message_history[room_id]:
            await websocket.send_text(message)

    def broadcast(self, room_id: str, message: str):
        for connection in self.active_connections[room_id]:
            connection.send_text(message)

    async def send_message(self, room_id: str, message: str, user: str):
        current_time = time.time()
        last_sent = self.message_timestamps[room_id][user]
        if current_time - last_sent < 1:
            return False
        self.message_timestamps[room_id][user] = current_time
        self.message_history[room_id].append(message)
        self.broadcast(room_id, message)
        return True

manager = ConnectionManager()

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if not await manager.send_message(room_id, data, str(websocket.client)):
                await websocket.send_text("You are sending messages too quickly. Please wait a second.")
    except WebSocketDisconnect:
        manager.active_connections[room_id].remove(websocket)
        manager.broadcast(room_id, f"{websocket.client} left")

@app.get("/")
def get():
    return HTMLResponse("<html><body><h1>WebSocket Chat</h1></body></html>")
