from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><title>Chat</title></head><body><h1>Chat Room</h1><div id='messages'></div><input id='input' type='text' placeholder='Type a message...'><script>const input = document.getElementById('input');const messages = document.getElementById('messages');input.addEventListener('keypress', (e) => {if (e.key === 'Enter') {const msg = input.value;messages.innerHTML += `<p>${msg}</p>`;input.value = '';}});</script></body></html>"
