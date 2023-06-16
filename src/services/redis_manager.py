from redis import asyncio as aioredis


async def get_redis():
    redis = await aioredis.from_url("redis://localhost:6379", max_connections=100)
    return redis
