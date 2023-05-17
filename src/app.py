from fastapi_profiler import PyInstrumentProfilerMiddleware
from sqladmin import Admin
from admin.auth import AdminAuth
from admin.schemas import UserAdmin, UniversityAdmin, SectionAdmin, RoleAdmin, QuestionAdmin, FeedbackAdmin
from auth.router import auth_router
from config import SECRET_KEY
from database import engine
from feedback.router import feedback_router
from question.router import question_router
from quiz.router import quiz_router
from section.router import section_router
from university.router import university_router
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
    app.state.selected_questions_id = set()


admin.add_view(UserAdmin)
admin.add_view(RoleAdmin)
admin.add_view(SectionAdmin)
admin.add_view(UniversityAdmin)
admin.add_view(QuestionAdmin)
admin.add_view(FeedbackAdmin)

app.include_router(auth_router)
app.include_router(question_router)
app.include_router(quiz_router)
app.include_router(section_router)
app.include_router(university_router)
app.include_router(feedback_router)
