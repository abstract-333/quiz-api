from sqladmin import Admin
from auth.auth_router import auth_router
from feedback.feedback_router import feedback_router
from question.question_router import question_router
from quiz.quiz_router import quiz_router
from rating.rating_router import rating_router
from section.section_router import section_router
from university.university_router import university_router
from admin.admin_auth import AdminAuth
from admin.admin_schemas import UserAdmin, UniversityAdmin, SectionAdmin, RoleAdmin, \
    QuestionAdmin, FeedbackAdmin, RatingAdmin
from config import SECRET_KEY
from database import engine
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi import FastAPI
app: FastAPI = FastAPI(
    title="Quiz App",
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

# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# app.add_middleware(SlowAPIMiddleware)
# limiter = Limiter(key_func=get_remote_address, default_limits=["30/minute"],
#                   storage_uri="redis://localhost:6379")

authentication_backend = AdminAuth(secret_key=SECRET_KEY)
admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)


# app.add_middleware(PyInstrumentProfilerMiddleware)


@app.on_event("startup")
async def startup_event():
    redis = await aioredis.from_url("redis://localhost:6379", max_connections=100)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    # await FastAPILimiter.init(redis, prefix="limiter")
    # app.state.limiter = limiter


@app.on_event("shutdown")
async def startup_event():
    await FastAPICache.clear()
    # await FastAPILimiter.close()


admin.add_view(UserAdmin)
admin.add_view(RoleAdmin)
admin.add_view(QuestionAdmin)
admin.add_view(RatingAdmin)
admin.add_view(FeedbackAdmin)
admin.add_view(SectionAdmin)
admin.add_view(UniversityAdmin)

app.include_router(auth_router)
app.include_router(question_router)
app.include_router(quiz_router)
app.include_router(rating_router)
app.include_router(feedback_router)
app.include_router(section_router)
app.include_router(university_router)
# @app.get("/")
# async def get_address(request: Request):
#     if not throttler.consume(identifier="user_id"):
#         return "NULLLLLLLLLL"
#     ip_address = request.client.host
#     ip_address = "78.110.106.250"
#
#     params = urllib.parse.urlencode({
#         'key': f'{API_KEY}',
#         'ip': f'{ip_address}',
#         # 'localityLanguage': 'ar',
#     })
#     async with aiohttp.ClientSession() as session:
#         async with session.get('https://api-bdc.net/data/country-by-ip', params=params) as response:
#             data = await response.json()
#
#     return data
