from redis import asyncio

redis: asyncio.Redis | None = None


async def get_redis() -> asyncio.Redis:
    return redis
