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

    def disconnect(self, room_id: str, websocket: WebSocket):
        self.active_connections[room_id].remove(websocket)
        self.broadcast(room_id, f"{websocket.client} left")

    def broadcast(self, room_id: str, message: str):
        for connection in self.active_connections[room_id]:
            connection.send_text(message)
        self.store_message(room_id, message)

    def store_message(self, room_id: str, message: str):
        self.message_history[room_id].append(message)
        if len(self.message_history[room_id]) > 50:
            self.message_history[room_id].pop(0)

    async def send_history(self, room_id: str, websocket: WebSocket):
        history = self.message_history[room_id]
        for message in history:
            await websocket.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            manager.broadcast(room_id, data)
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)

@app.get("/")
def get():
    return HTMLResponse("<html><body><h1>WebSocket Chat</h1></body></html>")