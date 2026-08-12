from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from collections import defaultdict
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time

app = FastAPI()

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    room = Column(String, index=True)
    user = Column(String)
    content = Column(String)

clients = defaultdict(list)
rooms = defaultdict(list)

@app.websocket("/ws/{room_name}")
def websocket_endpoint(websocket: WebSocket, room_name: str):
    await websocket.accept()
    clients[room_name].append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("/kick "):
                user_to_kick = data.split()[1]
                await kick_user(room_name, user_to_kick)
            elif data.startswith("/clear"):
                await clear_history(room_name)
            elif data.startswith("/rename "):
                new_room_name = data.split()[1]
                await rename_room(room_name, new_room_name)
            else:
                await broadcast(room_name, f"{data}")
    except WebSocketDisconnect:
        clients[room_name].remove(websocket)

async def kick_user(room_name, user):
    clients[room_name] = [ws for ws in clients[room_name] if ws != user]

async def clear_history(room_name):
    pass  # Implement clearing history logic

async def rename_room(old_name, new_name):
    clients[new_name] = clients.pop(old_name)

async def broadcast(room_name, message):
    for client in clients[room_name]:
        await client.send_text(message)

@app.get("/")
def get():
    return HTMLResponse(content="<html><body><h1>WebSocket Chat</h1></body></html>")