import redis.asyncio as redis
from typing import Optional
import json

from app.config import settings

# Global Redis client
_redis_client: Optional[redis.Redis] = None

async def get_redis_client() -> redis.Redis:
    """Get async Redis connection"""
    global _redis_client
    if _redis_client is None:
        _redis_client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return _redis_client

async def close_redis():
    """Close Redis connection"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None

# Simple cache operations
async def cache_set(key: str, value: str, expire: int = 300):
    """Set cache value (default 5 min expiry)"""
    client = await get_redis_client()
    await client.setex(key, expire, value)

async def cache_get(key: str) -> Optional[str]:
    """Get cache value"""
    client = await get_redis_client()
    return await client.get(key)

async def cache_delete(key: str):
    """Delete cache key"""
    client = await get_redis_client()
    await client.delete(key)

async def cache_exists(key: str) -> bool:
    """Check if key exists"""
    client = await get_redis_client()
    return await client.exists(key) > 0

# JSON helpers
async def cache_set_json(key: str, value: dict, expire: int = 300):
    """Set JSON object in cache"""
    await cache_set(key, json.dumps(value), expire)

async def cache_get_json(key: str) -> Optional[dict]:
    """Get JSON object from cache"""
    data = await cache_get(key)
    return json.loads(data) if data else None
