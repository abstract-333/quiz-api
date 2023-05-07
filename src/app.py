from sqladmin import Admin
from admin.schemas import UserAdmin, UniversityAdmin, AdminAuth
from auth.router import auth_router
from config import SECRET_KEY
from database import engine
from quiz.router import quiz_router
from university.router import university_router
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi import FastAPI

app = FastAPI(
    title="Students App",
)
authentication_backend = AdminAuth(secret_key=SECRET_KEY)
admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)

# app.add_middleware(PyInstrumentProfilerMiddleware)


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


# admin.add_view(UserAdmin)
admin.add_view(UniversityAdmin)

app.include_router(auth_router)
app.include_router(quiz_router)
app.include_router(university_router)
