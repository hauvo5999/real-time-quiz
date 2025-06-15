# main.py - FastAPI Real-Time Leaderboard Server
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Set
import redis.asyncio as redis
import json
import asyncio
import logging
from datetime import datetime
import uuid
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Elsa Real-Time Leaderboard",
    description="Real-time leaderboard system with WebSocket and Redis",
    version="1.0.0"
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic Models
class User(BaseModel):
    id: str
    username: str
    avatar: str
    color: str

class LeaderboardEntry(BaseModel):
    rank: int
    userId: str
    username: str
    avatar: str
    color: str
    score: int
    isConnected: bool

class ScoreUpdate(BaseModel):
    points: int

class JoinDemo(BaseModel):
    userId: str
    sessionId: str = "DEMO123"

class UserRank(BaseModel):
    userId: str
    score: int
    rank: Optional[int]

class LeaderboardUpdate(BaseModel):
    leaderboard: List[LeaderboardEntry]
    lastUpdate: Optional[Dict] = None

class SessionInfo(BaseModel):
    id: str
    title: str
    status: str
    participants: int

# Demo Users Data
demo_users = {
    'alice': User(id='alice', username='Alice', avatar='👩', color='#e91e63'),
    'bob': User(id='bob', username='Bob', avatar='👨', color='#2196f3'),
    'charlie': User(id='charlie', username='Charlie', avatar='🧑', color='#ff9800'),
    'diana': User(id='diana', username='Diana', avatar='👩‍🦱', color='#4caf50'),
    'eve': User(id='eve', username='Eve', avatar='👱‍♀️', color='#9c27b0'),
    'frank': User(id='frank', username='Frank', avatar='👨‍🦲', color='#795548')
}

# Global variables
connected_clients: Dict[str, WebSocket] = {}
user_sessions: Dict[str, str] = {}  # websocket_id -> user_id
session_participants: Dict[str, Set[str]] = {"DEMO123": set()}

# Redis connection with fallback to in-memory
redis_client: Optional[redis.Redis] = None
in_memory_leaderboard: Dict[str, Dict[str, int]] = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, str] = {}  # user_id -> connection_id

    async def connect(self, websocket: WebSocket, connection_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info(f"🔌 New connection: {connection_id}")

    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remove user mapping
        user_id = None
        for uid, cid in self.user_connections.items():
            if cid == connection_id:
                user_id = uid
                break
        
        if user_id:
            del self.user_connections[user_id]
            session_participants["DEMO123"].discard(user_id)
            logger.info(f"👋 User {user_id} disconnected")

    def map_user(self, user_id: str, connection_id: str):
        self.user_connections[user_id] = connection_id
        session_participants["DEMO123"].add(user_id)

    async def send_personal_message(self, message: dict, connection_id: str):
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")

    async def broadcast_to_session(self, message: dict, session_id: str = "DEMO123"):
        """Broadcast message to all users in a session"""
        for user_id in session_participants.get(session_id, set()):
            connection_id = self.user_connections.get(user_id)
            if connection_id and connection_id in self.active_connections:
                try:
                    await self.active_connections[connection_id].send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to {user_id}: {e}")

manager = ConnectionManager()

class LeaderboardService:
    def __init__(self):
        self.session_key = lambda session_id: f"leaderboard:{session_id}"

    async def update_score(self, session_id: str, user_id: str, score: int) -> bool:
        """Update user score in leaderboard"""
        try:
            if redis_client:
                await redis_client.zadd(self.session_key(session_id), {user_id: score})
                await redis_client.expire(self.session_key(session_id), 3600)  # 1 hour expiry
            else:
                # Fallback to in-memory storage
                if session_id not in in_memory_leaderboard:
                    in_memory_leaderboard[session_id] = {}
                in_memory_leaderboard[session_id][user_id] = score
            
            logger.info(f"📊 Score updated: {user_id} = {score} points in {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating score: {e}")
            return False

    async def get_leaderboard(self, session_id: str, limit: int = 20) -> List[LeaderboardEntry]:
        """Get current leaderboard with user details"""
        try:
            results = []
            
            if redis_client:
                # Get users with scores in descending order from Redis
                redis_results = await redis_client.zrevrange(
                    self.session_key(session_id), 0, limit - 1, withscores=True
                )
                
                for user_id, score in redis_results:
                    if isinstance(user_id, bytes):
                        user_id = user_id.decode()
                    results.append({"userId": user_id, "score": int(score)})
            else:
                # Fallback to in-memory storage
                session_data = in_memory_leaderboard.get(session_id, {})
                results = [
                    {"userId": user_id, "score": score}
                    for user_id, score in sorted(session_data.items(), key=lambda x: x[1], reverse=True)
                ][:limit]
            
            # Add user details and ranking
            leaderboard = []
            for index, item in enumerate(results):
                user = demo_users.get(item["userId"])
                if not user:
                    user = User(
                        id=item["userId"],
                        username=f"User {item['userId']}",
                        avatar="👤",
                        color="#666666"
                    )
                
                leaderboard.append(LeaderboardEntry(
                    rank=index + 1,
                    userId=item["userId"],
                    username=user.username,
                    avatar=user.avatar,
                    color=user.color,
                    score=item["score"],
                    isConnected=item["userId"] in session_participants.get(session_id, set())
                ))
            
            return leaderboard
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []

    async def get_user_rank(self, session_id: str, user_id: str) -> UserRank:
        """Get user's current rank and score"""
        try:
            score = 0
            rank = None
            
            if redis_client:
                redis_score = await redis_client.zscore(self.session_key(session_id), user_id)
                redis_rank = await redis_client.zrevrank(self.session_key(session_id), user_id)
                score = int(redis_score) if redis_score else 0
                rank = redis_rank + 1 if redis_rank is not None else None
            else:
                session_data = in_memory_leaderboard.get(session_id, {})
                score = session_data.get(user_id, 0)
                
                # Calculate rank from in-memory data
                sorted_users = sorted(session_data.items(), key=lambda x: x[1], reverse=True)
                for index, (uid, _) in enumerate(sorted_users):
                    if uid == user_id:
                        rank = index + 1
                        break
            
            return UserRank(userId=user_id, score=score, rank=rank)
        except Exception as e:
            logger.error(f"Error getting user rank: {e}")
            return UserRank(userId=user_id, score=0, rank=None)

# Initialize services
leaderboard_service = LeaderboardService()

async def init_redis():
    """Initialize Redis connection with fallback"""
    global redis_client
    try:
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        await redis_client.ping()
        logger.info("✅ Connected to Redis - Using Redis for leaderboard storage")
    except Exception as e:
        logger.warning(f"⚠️  Redis not available - Using in-memory storage: {e}")
        redis_client = None

@app.on_event("startup")
async def startup_event():
    await init_redis()

@app.on_event("shutdown")
async def shutdown_event():
    if redis_client:
        await redis_client.close()

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    connection_id = str(uuid.uuid4())
    await manager.connect(websocket, connection_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            event_type = message.get("type")
            event_data = message.get("data", {})
            
            if event_type == "join-demo":
                await handle_join_demo(connection_id, event_data)
            elif event_type == "update-score":
                await handle_update_score(connection_id, event_data)
            else:
                await manager.send_personal_message({
                    "type": "error",
                    "data": {"message": f"Unknown event type: {event_type}"}
                }, connection_id)
                
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        
        # Notify other users about disconnect
        user_id = None
        for uid, cid in manager.user_connections.items():
            if cid == connection_id:
                user_id = uid
                break
        
        if user_id and user_id in demo_users:
            await manager.broadcast_to_session({
                "type": "participant-left",
                "data": {
                    "userId": user_id,
                    "username": demo_users[user_id].username,
                    "totalParticipants": len(session_participants["DEMO123"])
                }
            })

async def handle_join_demo(connection_id: str, data: dict):
    """Handle user joining demo"""
    user_id = data.get("userId")
    session_id = data.get("sessionId", "DEMO123")
    
    if user_id not in demo_users:
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": "Invalid user ID. Use: alice, bob, charlie, diana, eve, or frank"}
        }, connection_id)
        return
    
    # Map user to connection
    manager.map_user(user_id, connection_id)
    
    logger.info(f"👥 {user_id} joined leaderboard demo")
    
    # Send current leaderboard
    leaderboard = await leaderboard_service.get_leaderboard(session_id)
    await manager.send_personal_message({
        "type": "leaderboard-update",
        "data": {
            "leaderboard": [entry.dict() for entry in leaderboard],
            "sessionInfo": {
                "id": session_id,
                "title": "English Grammar Challenge",
                "status": "active",
                "participants": len(session_participants[session_id])
            }
        }
    }, connection_id)
    
    # Send user's current rank
    user_rank = await leaderboard_service.get_user_rank(session_id, user_id)
    await manager.send_personal_message({
        "type": "user-rank-update",
        "data": user_rank.dict()
    }, connection_id)
    
    # Notify other users
    await manager.broadcast_to_session({
        "type": "participant-joined",
        "data": {
            "userId": user_id,
            "username": demo_users[user_id].username,
            "avatar": demo_users[user_id].avatar,
            "totalParticipants": len(session_participants[session_id])
        }
    })

async def handle_update_score(connection_id: str, data: dict):
    """Handle score update"""
    points = data.get("points", 0)
    
    # Find user_id from connection
    user_id = None
    for uid, cid in manager.user_connections.items():
        if cid == connection_id:
            user_id = uid
            break
    
    if not user_id:
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": "Not connected to demo session"}
        }, connection_id)
        return
    
    session_id = "DEMO123"
    
    # Get current score and add points
    current_rank = await leaderboard_service.get_user_rank(session_id, user_id)
    new_score = current_rank.score + points
    
    # Update leaderboard
    await leaderboard_service.update_score(session_id, user_id, new_score)
    
    # Get updated leaderboard and broadcast to all users
    updated_leaderboard = await leaderboard_service.get_leaderboard(session_id)
    updated_user_rank = await leaderboard_service.get_user_rank(session_id, user_id)
    
    await manager.broadcast_to_session({
        "type": "leaderboard-update",
        "data": {
            "leaderboard": [entry.dict() for entry in updated_leaderboard],
            "lastUpdate": {
                "userId": user_id,
                "username": demo_users[user_id].username,
                "pointsEarned": points,
                "newScore": new_score,
                "oldRank": current_rank.rank,
                "newRank": updated_user_rank.rank
            }
        }
    })
    
    # Send updated rank to user
    await manager.send_personal_message({
        "type": "user-rank-update",
        "data": updated_user_rank.dict()
    }, connection_id)
    
    logger.info(f"🎯 {user_id} scored {points} points (total: {new_score})")

# REST API Endpoints

@app.get("/")
async def read_root():
    """Serve demo page"""
    try:
        with open("static/index.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <body>
                <h1>Demo files not found</h1>
                <p>Please make sure static/index.html exists</p>
                <p>Or go to <a href="/docs">API Documentation</a></p>
            </body>
        </html>
        """)

@app.get("/api/demo")
async def get_demo_info():
    """Get demo information"""
    return {
        "title": "Real-Time Leaderboard Demo",
        "description": "Demonstration of real-time leaderboard updates using WebSocket and Redis",
        "features": [
            "Real-time score updates",
            "Live ranking changes",
            "Participant notifications", 
            "WebSocket communication",
            "Redis-powered leaderboard"
        ],
        "availableUsers": [user.dict() for user in demo_users.values()],
        "activeSessions": {
            "DEMO123": {
                "id": "DEMO123",
                "title": "English Grammar Challenge",
                "status": "active",
                "participants": len(session_participants["DEMO123"])
            }
        }
    }

@app.get("/api/leaderboard/{session_id}")
async def get_leaderboard(session_id: str, limit: int = 20):
    """Get current leaderboard"""
    leaderboard = await leaderboard_service.get_leaderboard(session_id, limit)
    return {
        "sessionId": session_id,
        "leaderboard": [entry.dict() for entry in leaderboard],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/demo/populate")
async def populate_demo():
    """Populate demo data"""
    session_id = "DEMO123"
    
    # Sample data for demo
    sample_data = [
        {"userId": "alice", "score": 145},
        {"userId": "bob", "score": 132},
        {"userId": "charlie", "score": 128},
        {"userId": "diana", "score": 115},
        {"userId": "eve", "score": 98},
        {"userId": "frank", "score": 87}
    ]
    
    for data in sample_data:
        await leaderboard_service.update_score(session_id, data["userId"], data["score"])
    
    leaderboard = await leaderboard_service.get_leaderboard(session_id)
    
    # Broadcast update to all connected clients
    await manager.broadcast_to_session({
        "type": "leaderboard-update",
        "data": {
            "leaderboard": [entry.dict() for entry in leaderboard],
            "lastUpdate": {
                "type": "demo_data_populated",
                "message": "Demo data populated!"
            }
        }
    })
    
    return {
        "message": "Demo data populated successfully",
        "leaderboard": [entry.dict() for entry in leaderboard]
    }

@app.post("/api/demo/reset")
async def reset_demo():
    """Reset leaderboard"""
    session_id = "DEMO123"
    
    try:
        if redis_client:
            await redis_client.delete(f"leaderboard:{session_id}")
        else:
            in_memory_leaderboard[session_id] = {}
        
        leaderboard = await leaderboard_service.get_leaderboard(session_id)
        
        # Broadcast reset to all connected clients
        await manager.broadcast_to_session({
            "type": "leaderboard-update",
            "data": {
                "leaderboard": [entry.dict() for entry in leaderboard],
                "lastUpdate": {
                    "type": "leaderboard_reset",
                    "message": "Leaderboard reset!"
                }
            }
        })
        
        return {
            "message": "Leaderboard reset successfully",
            "leaderboard": [entry.dict() for entry in leaderboard]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to reset leaderboard")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "storage": "Redis" if redis_client else "In-Memory",
        "connectedUsers": len(session_participants["DEMO123"]),
        "activeConnections": len(manager.active_connections)
    }

if __name__ == "__main__":
    import uvicorn
    
    print("""
🚀 FastAPI Real-Time Leaderboard Demo Server
📍 URL: http://localhost:8000
💾 Storage: Redis with In-Memory fallback
🎯 Ready for demonstration!

📋 Demo Instructions:
1. Open http://localhost:8000 in multiple browser tabs
2. Select different users (alice, bob, charlie, etc.) in each tab
3. Click "Add Points" to simulate score updates
4. Watch real-time leaderboard updates across all tabs
5. Use "Populate Demo Data" and "Reset" for easy demo setup

📚 API Documentation: http://localhost:8000/docs
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
