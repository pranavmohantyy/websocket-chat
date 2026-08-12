# WebSocket Chat

## Overview
A real-time multi-room chat server built with FastAPI WebSockets and a browser client.

## WebSocket Protocol

### Connection
- Client connects to the server using WebSocket.

### Join Room
- Send a message to join a room: `{ "action": "join", "room": "room_name", "user": "username" }`

### Send Message
- To send a message: `{ "action": "message", "room": "room_name", "user": "username", "content": "your_message" }`

### Receive Message
- Messages are broadcasted to all users in the room.

### Leave Room
- To leave a room: `{ "action": "leave", "room": "room_name", "user": "username" }`

## Running the Server
1. Install dependencies: `pip install fastapi sqlalchemy`
2. Run the server: `uvicorn main:app --reload`

## Client
Use the provided HTML client to connect and chat.