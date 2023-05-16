import itertools
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from fastapi_cache.decorator import cache
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from numpy import random as num_random
from starlette import status
from auth.base_config import current_user
from auth.models import User
from database import get_async_session
from question.models import question
from utils.custom_exceptions import InvalidPage
from utils.error_code import ErrorCode
from utils.result_into_list import ResultIntoList

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
                    ErrorCode.INVALID_PAGE: {
                        "summary": "Invalid page",
                        "value": {"detail": ErrorCode.INVALID_PAGE},
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
            raise InvalidPage

        number_software_questions = number_questions * 0.6
        number_network_questions = number_questions * 0.2
        number_ai_questions = number_questions * 0.2

        software_query = select(question).where(question.c.section_id == 1).order_by(func.random()).limit(
            number_software_questions)
        network_query = select(question).where(question.c.section_id == 2).order_by(func.random()).limit(
            number_network_questions)
        ai_query = select(question).where(question.c.section_id == 3).order_by(func.random()).limit(number_ai_questions)

        software = await session.execute(software_query)
        network = await session.execute(network_query)
        ai = await session.execute(ai_query)

        software = ResultIntoList(result_proxy=software)
        network = ResultIntoList(result_proxy=network)
        ai = ResultIntoList(result_proxy=ai)

        result = list(itertools.chain(software.parse(), network.parse(), ai.parse()))

        num_random.shuffle(result)

        return {"status": "success",
                "data": result,
                "details": None
                }

    except InvalidPage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.INVALID_PAGE)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
