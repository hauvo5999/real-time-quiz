import json
from typing import List, Dict, Optional
import aioredis
from fastapi import WebSocket

class RedisService:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = aioredis.from_url(redis_url, decode_responses=True)
        self.pubsub = self.redis.pubsub()

    async def add_user_to_leaderboard(self, quiz_id: str, user_id: str, username: str, score: int = 0):
        """Add or update user score in the leaderboard"""
        # Add to sorted set for ranking
        await self.redis.zadd(f"leaderboard:{quiz_id}", {user_id: score})
        # Store user info
        await self.redis.hset(f"user_info:{quiz_id}", user_id, username)

    async def get_leaderboard(self, quiz_id: str, start: int = 0, end: int = -1) -> List[Dict]:
        """Get leaderboard rankings with user info"""
        # Get top scores with ranks
        scores = await self.redis.zrevrange(f"leaderboard:{quiz_id}", start, end, withscores=True)
        # Get user info
        user_info = await self.redis.hgetall(f"user_info:{quiz_id}")
        
        leaderboard = []
        for rank, (user_id, score) in enumerate(scores, start=1):
            leaderboard.append({
                "rank": rank,
                "user_id": user_id,
                "username": user_info.get(user_id, "Unknown"),
                "score": int(score)
            })
        return leaderboard

    async def update_score(self, quiz_id: str, user_id: str, score: int):
        """Update user's score and broadcast to all subscribers"""
        # Update score in sorted set
        await self.redis.zadd(f"leaderboard:{quiz_id}", {user_id: score})
        # Get updated leaderboard
        leaderboard = await self.get_leaderboard(quiz_id)
        # Publish update to quiz channel
        await self.redis.publish(f"quiz:{quiz_id}:leaderboard", json.dumps(leaderboard))

    async def subscribe_to_leaderboard(self, quiz_id: str, websocket: WebSocket):
        """Subscribe to leaderboard updates for a quiz"""
        await self.pubsub.subscribe(f"quiz:{quiz_id}:leaderboard")
        try:
            while True:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                if message and message["type"] == "message":
                    await websocket.send_text(message["data"])
        except Exception as e:
            print(f"Error in leaderboard subscription: {e}")
        finally:
            await self.pubsub.unsubscribe(f"quiz:{quiz_id}:leaderboard")

    async def remove_user_from_leaderboard(self, quiz_id: str, user_id: str):
        """Remove user from leaderboard"""
        await self.redis.zrem(f"leaderboard:{quiz_id}", user_id)
        await self.redis.hdel(f"user_info:{quiz_id}", user_id)

    async def clear_leaderboard(self, quiz_id: str):
        """Clear all leaderboard data for a quiz"""
        await self.redis.delete(f"leaderboard:{quiz_id}")
        await self.redis.delete(f"user_info:{quiz_id}")

# Create a singleton instance
redis_service = RedisService() 