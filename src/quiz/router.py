from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from fastapi_cache.decorator import cache
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from sqlalchemy.ext.asyncio import AsyncSession
from numpy import random as num_random
from starlette import status
from database import get_async_session
from quiz.quiz_db import get_quiz_db
from utils.custom_exceptions import InvalidPage, QuestionsInvalidNumber
from utils.error_code import ErrorCode

quiz_router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"]
)

GET_QUIZ_RESPONSES: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.QUESTIONS_NUMBER_INVALID: {
                        "summary": "Invalid number of questions",
                        "value": {"detail": ErrorCode.QUESTIONS_NUMBER_INVALID},
                    }
                }
            },
        },
    },
    status.HTTP_403_FORBIDDEN: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.USER_NOT_AUTHENTICATED: {
                    "summary": "Not authenticated",
                    "value": {"detail": "Not authenticated"},
                }}
            },
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal sever error.",
    }
}


# @cache(expire=60 * 10)
@quiz_router.get("/get", name="quiz:get quiz", dependencies=[Depends(HTTPBearer())], responses=GET_QUIZ_RESPONSES)
async def get_quiz(number_questions: int = 50, session: AsyncSession = Depends(get_async_session)):
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

    except InvalidPage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.QUESTIONS_NUMBER_INVALID)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


