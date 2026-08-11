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
    timestamp = Column(DateTime)

DATABASE_URL = "sqlite:///./messages.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

rooms = defaultdict(list)

class ConnectionManager:
    def __init__(self):
        self.active_connections = defaultdict(list)

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[room_id].append(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket):
        self.active_connections[room_id].remove(websocket)

    async def send_message(self, room_id: str, message: str):
        for connection in self.active_connections[room_id]:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            timestamp = time.time()
            message = Message(room=room_id, user="user", content=data, timestamp=timestamp)
            with SessionLocal() as db:
                db.add(message)
                db.commit()
            await manager.send_message(room_id, data)
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)

@app.get("/")
def get():
    return HTMLResponse(content="<html><body><h1>WebSocket Chat</h1></body></html>")
