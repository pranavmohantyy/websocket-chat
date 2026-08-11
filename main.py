from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from collections import defaultdict

app = FastAPI()

rooms = defaultdict(list)

class ConnectionManager:
    def __init__(self):
        self.active_connections = defaultdict(list)

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[room_id].append(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket):
        self.active_connections[room_id].remove(websocket)

    def get_connections(self, room_id: str):
        return self.active_connections[room_id]

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><title>Chat</title></head><body><h1>Chat Room</h1><div id='messages'></div><input id='input' type='text' placeholder='Type a message...'><script>const input = document.getElementById('input');const messages = document.getElementById('messages');input.addEventListener('keypress', async (e) => {if (e.key === 'Enter') {const message = input.value;input.value = '';await fetch('/send', {method: 'POST', body: JSON.stringify({msg: message})});}});</script></body></html>"
