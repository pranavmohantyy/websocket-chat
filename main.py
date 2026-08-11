from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from collections import defaultdict

app = FastAPI()

rooms = defaultdict(list)

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><title>Chat</title></head><body><h1>Chat Room</h1><div id='messages'></div><input id='input' type='text' placeholder='Type a message...'><script>const input = document.getElementById('input');const messages = document.getElementById('messages');input.addEventListener('keypress', (e) => {if (e.key === 'Enter') {const msg = input.value;messages.innerHTML += `<p>${msg}</p>`;input.value = '';}});</script></body></html>"

@app.websocket("/ws/{room}/{username}")
async def websocket_endpoint(websocket: WebSocket, room: str, username: str):
    await websocket.accept()
    rooms[room].append((username, websocket))
    try:
        while True:
            data = await websocket.receive_text()
            for user, conn in rooms[room]:
                if conn != websocket:
                    await conn.send_text(f"{username}: {data}")
    except WebSocketDisconnect:
        rooms[room].remove((username, websocket))