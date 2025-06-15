from typing import List, Dict
from app.core.redis import get_redis
from app.models.user import User
from app.models.leaderboard import Leaderboard
from app.schemas.leaderboard import LeaderboardResponse, LeaderboardUpdateMessage
import json
import asyncio

class LeaderboardService:
    def __init__(self):
        self.REDIS_EXPIRATION_TIME = 60 * 5  # 5 minutes
        self.USER_SCORE_KEY = "quiz:{quiz_id}:user:{username}:score"
        self.LEADERBOARD_CHANNEL = "leaderboard:{quiz_id}"
        self._subscribers = {}

    async def join_leaderboard(self, quiz_id: str, user: User):
        """Join leaderboard for a quiz"""
        redis = await get_redis()
        score_key = self.USER_SCORE_KEY.format(quiz_id=quiz_id, username=user.username)
        if not await redis.get(score_key):
            await redis.set(score_key, 0, ex=self.REDIS_EXPIRATION_TIME)
        print(f'score_key: {score_key}')
        print(f'redis: {redis}')

    async def subscribe(self, quiz_id: str, websocket):
        """Subscribe to leaderboard updates for a quiz"""
        redis = await get_redis()
        channel = self.LEADERBOARD_CHANNEL.format(quiz_id=quiz_id)
        
        if quiz_id not in self._subscribers:
            self._subscribers[quiz_id] = set()
            # Start listening to Redis channel
            asyncio.create_task(self._listen_to_channel(quiz_id))
        
        self._subscribers[quiz_id].add(websocket)

    def unsubscribe(self, quiz_id: str, websocket):
        """Unsubscribe from leaderboard updates"""
        if quiz_id in self._subscribers:
            self._subscribers[quiz_id].discard(websocket)
            if not self._subscribers[quiz_id]:
                del self._subscribers[quiz_id]

    async def _listen_to_channel(self, quiz_id: str):
        """Listen to Redis channel for leaderboard updates"""
        redis = await get_redis()
        channel = self.LEADERBOARD_CHANNEL.format(quiz_id=quiz_id)
        
        try:
            pubsub = redis.pubsub()
            await pubsub.subscribe(channel)
            
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message and message["type"] == "message":
                    # Broadcast to all subscribers
                    await self._broadcast_to_subscribers(quiz_id, message["data"])
        except Exception as e:
            print(f"Error in Redis subscription for quiz {quiz_id}: {str(e)}")

    async def _broadcast_to_subscribers(self, quiz_id: str, message_data):
        """Broadcast message to all subscribers"""
        if quiz_id not in self._subscribers:
            return
            
        for websocket in self._subscribers[quiz_id]:
            try:
                await websocket.send_text(message_data)
            except Exception as e:
                print(f"Error broadcasting to subscriber: {str(e)}")

    async def get_leaderboard(self, quiz_id: str) -> List[Dict]:
        """Get current leaderboard for a quiz"""
        redis = await get_redis()
        
        try:
            # Get all user scores from Redis
            pattern = self.USER_SCORE_KEY.format(quiz_id=quiz_id, username="*")
            keys = await redis.keys(pattern)
            print(f'Keys: {keys}')
            
            # Build leaderboard
            leaderboard = []
            for key in keys:
                username = key.split(":")[-2]  # Extract username from key
                score = int(await redis.get(key) or 0)
                leaderboard.append({
                    "username": username,
                    "score": score
                })
            
            # Sort by score
            leaderboard.sort(key=lambda x: x["score"], reverse=True)
            
            # Add ranks
            for i, entry in enumerate(leaderboard):
                entry["rank"] = i + 1
            
            return leaderboard
            
        except Exception as e:
            print(f"Error getting leaderboard: {str(e)}")
            return []

    async def broadcast_leaderboard(self, quiz_id: str, active_connections: Dict[str, List]):
        """Broadcast leaderboard to all connected clients"""
        try:
            print(f'Active connections: {active_connections.items()}')
            if quiz_id not in active_connections:
                return
            
            leaderboard = await self.get_leaderboard(quiz_id)
            print(f"Leaderboard: {leaderboard}")
            
            # Create message
            message = {
                "type": "leaderboard_update",
                "data": leaderboard
            }
            
            # Publish to Redis channel
            redis = await get_redis()
            channel = self.LEADERBOARD_CHANNEL.format(quiz_id=quiz_id)
            await redis.publish(channel, json.dumps(message))
            
        except Exception as e:
            print(f"Error broadcasting leaderboard: {str(e)}")

# Initialize service
leaderboard_service = LeaderboardService() 