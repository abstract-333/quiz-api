from fastapi_profiler import PyInstrumentProfilerMiddleware
from sqladmin import Admin
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
authentication_backend = AdminAuth(secret_key=SECRET_KEY)
admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)

# app.add_middleware(PyInstrumentProfilerMiddleware)


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


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
