from fastapi_limiter import FastAPILimiter
from fastapi_profiler import PyInstrumentProfilerMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from sqladmin import Admin
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from admin.admin_auth import AdminAuth
from admin.admin_schemas import UserAdmin, UniversityAdmin, SectionAdmin, RoleAdmin, \
    QuestionAdmin, FeedbackAdmin, RatingAdmin
from auth.auth_router import auth_router
from config import SECRET_KEY
from database import engine
from feedback.feedback_router import feedback_router
from question.question_router import question_router
from quiz.quiz_router import quiz_router
from rating.rating_router import rating_router
from section.section_router import section_router
from university.university_router import university_router
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi import FastAPI

app = FastAPI(
    title="Quiz App",
)
# middleware to redirect HTTP to HTTPS
# app.add_middleware(HTTPSRedirectMiddleware)

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
# middleware to set secure HTTP headers
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
#     expose_headers=["X-Total-Count"],
#     allow_credentials=True,
# )
authentication_backend = AdminAuth(secret_key=SECRET_KEY)
admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)

# app.add_middleware(PyInstrumentProfilerMiddleware)

limiter = None


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    # await FastAPILimiter.init(redis, prefix="fastapi-cache")
    global limiter
    limiter = Limiter(key_func=get_remote_address, default_limits=["2/minute"], storage_uri="redis://localhost")
    app.state.limiter = limiter


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
