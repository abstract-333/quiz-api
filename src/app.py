from auth.router import auth_router
from quiz.router import quiz_router
from university.router import university_router
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi import FastAPI

app = FastAPI(
    title="Students App",
)


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

# app.mount_app(site)
app.include_router(auth_router)
app.include_router(quiz_router)
app.include_router(university_router)
