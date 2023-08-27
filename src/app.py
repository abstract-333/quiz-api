from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from sqladmin import Admin

from all_routers_and_views import all_routers, all_admin_views
from api.admin_panel.admin_auth import AdminAuth
from config import SECRET_KEY
from db.database import engine

app: FastAPI = FastAPI(
    title="Quiz App",
    version="1.0.0",
    # dependencies=[Depends(BucketLimiter())]
)

# middleware to redirect HTTP to HTTPS
# app.add_middleware(HTTPSRedirectMiddleware)

# middleware to set secure HTTP headers
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
#     expose_headers=["X-Total-Count"],
#     allow_credentials=True,
# )
#

authentication_backend = AdminAuth(secret_key=SECRET_KEY)
admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)


# app.add_middleware(PyInstrumentProfilerMiddleware)


@app.on_event("startup")
async def startup_event():
    redis = await aioredis.from_url("redis://localhost:6379", max_connections=100)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


@app.on_event("shutdown")
async def startup_event():
    await FastAPICache.clear()


for view in all_admin_views:
    admin.add_view(view)

for router in all_routers:
    app.include_router(router)
