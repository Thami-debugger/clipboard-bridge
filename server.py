import asyncio
import secrets
import time
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Clipboard Bridge - Copy between devices")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Room-based architecture for multi-user support
rooms: Dict[str, Dict] = {}  # room_code -> {clients: set, last_content: str, created_at: float}

class ClipboardData(BaseModel):
    room_code: str
    content: str

def generate_room_code() -> str:
    """Generate a 6-character room code"""
    return secrets.token_urlsafe(4).upper()[:6]

def cleanup_old_rooms():
    """Remove rooms older than 24 hours"""
    current_time = time.time()
    expired = [code for code, data in rooms.items() 
               if current_time - data["created_at"] > 86400]  # 24 hours
    for code in expired:
        del rooms[code]

@app.get("/")
def home():
    return HTMLResponse(open("static/index.html", encoding="utf-8").read())

@app.post("/create-room")
async def create_room():
    """Create a new room and return the room code"""
    cleanup_old_rooms()
    room_code = generate_room_code()
    while room_code in rooms:  # Ensure uniqueness
        room_code = generate_room_code()
    
    rooms[room_code] = {
        "clients": set(),
        "last_content": "",
        "created_at": time.time()
    }
    return {"room_code": room_code}

@app.post("/sync")
async def sync_clipboard(data: ClipboardData):
    """Sync clipboard content to all devices in the room"""
    if data.room_code not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = rooms[data.room_code]
    room["last_content"] = data.content
    
    # Broadcast to all connected WebSocket clients in this room
    await broadcast_to_room(data.room_code, data.content)
    
    return {"status": "synced", "devices": len(room["clients"])}

@app.get("/room/{room_code}/status")
async def room_status(room_code: str):
    """Get room status and device count"""
    if room_code not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    return {
        "room_code": room_code,
        "devices_connected": len(rooms[room_code]["clients"]),
        "last_content_length": len(rooms[room_code]["last_content"])
    }

@app.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    """WebSocket endpoint for real-time clipboard sync"""
    if room_code not in rooms:
        await websocket.close(code=1008, reason="Room not found")
        return
    
    await websocket.accept()
    rooms[room_code]["clients"].add(websocket)
    
    try:
        # Send the last content when client connects
        if rooms[room_code]["last_content"]:
            await websocket.send_json({
                "type": "sync",
                "content": rooms[room_code]["last_content"]
            })
        
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "clipboard":
                content = data.get("content", "")
                rooms[room_code]["last_content"] = content
                # Broadcast to all other clients in the room
                await broadcast_to_room(room_code, content, exclude=websocket)
    
    except WebSocketDisconnect:
        rooms[room_code]["clients"].remove(websocket)

async def broadcast_to_room(room_code: str, content: str, exclude: WebSocket = None):
    """Broadcast content to all clients in a room"""
    if room_code not in rooms:
        return
    
    dead_clients = []
    for client in rooms[room_code]["clients"]:
        if client != exclude:
            try:
                await client.send_json({"type": "sync", "content": content})
            except:
                dead_clients.append(client)
    
    # Remove dead connections
    for client in dead_clients:
        rooms[room_code]["clients"].discard(client)

@app.on_event("startup")
async def startup():
    """Startup tasks"""
    pass
