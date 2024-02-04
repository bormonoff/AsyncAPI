from typing import Optional

from redis import asyncio

redis: Optional[asyncio.Redis] = None

async def get_redis() -> asyncio.Redis:
    return redis
