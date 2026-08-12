from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from collections import defaultdict
from sqlalchemy import create_engine, Column, String, Integer
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

@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await websocket.accept()
    clients[room].append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            if message_data['action'] == 'message':
                for client in clients[room]:
                    await client.send_text(data)
    except WebSocketDisconnect:
        clients[room].remove(websocket)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))