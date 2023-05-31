from fastapi import APIRouter, Depends, HTTPException, FastAPI
from fastapi.security import HTTPBearer
from fastapi_cache.decorator import cache
from fastapi_limiter.depends import RateLimiter
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from numpy import random as num_random
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from auth.base_config import current_user
from auth.auth_models import User
from database import get_async_session
from quiz.quiz_docs import GET_QUIZ_RESPONSES
from quiz.quiz_db import get_quiz_db
from utils.custom_exceptions import QuestionsInvalidNumber
from utils.error_code import ErrorCode


quiz_app = FastAPI()
quiz_router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"]
)
# quiz_router.include_router(quiz_app)
#
# limiter = Limiter(key_func=get_remote_address)
# quiz_app.state.limiter = limiter
# quiz_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# limiter.slowapi_startup()


@cache(expire=60 * 100)
# @limiter.limit("100/10second")
@quiz_router.get("/get", name="quiz:get quiz",
                 dependencies=[Depends(HTTPBearer())], responses=GET_QUIZ_RESPONSES)
async def get_quiz(request: Request, response: Response, number_questions: int = 50,
                   verified_user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    try:
        if number_questions not in range(10, 51):
            raise QuestionsInvalidNumber

        number_software_questions = int(number_questions * 0.6)
        number_network_questions = int(number_questions * 0.2)
        number_ai_questions = int(number_questions * 0.2)

        result = await get_quiz_db(number_ai_questions=number_ai_questions,
                                   number_network_questions=number_network_questions,
                                   number_software_questions=number_software_questions,
                                   session=session)

        num_random.shuffle(result)

        return {"status": "success",
                "data": result,
                "details": None
                }

    except QuestionsInvalidNumber:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.QUESTIONS_NUMBER_INVALID)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
