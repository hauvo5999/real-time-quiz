from redis import asyncio as aioredis
from app.core.config import settings

async def get_redis():
    redis = await aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
        encoding="utf-8",
        decode_responses=True
    )
    return redis 
