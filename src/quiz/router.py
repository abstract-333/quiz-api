import itertools

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from fastapi_cache.decorator import cache
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from numpy import random as num_random
from starlette import status

from auth.base_config import current_user
from auth.models import User
from database import get_async_session
from question.models import QUESTIONS_SECTIONS
from utils.result_into_list import ResultIntoList

quiz_router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"]
)


# @cache(expire=60 * 10)
@quiz_router.get("/get", name="question:get question", )
async def get_quiz(session: AsyncSession = Depends(get_async_session)):
    try:
        software_table = QUESTIONS_SECTIONS[0]
        network_table = QUESTIONS_SECTIONS[1]
        ai_table = QUESTIONS_SECTIONS[2]
        first_query = select(software_table).order_by(func.random())
        second_query = select(network_table).order_by(func.random())
        third_query = select(ai_table).order_by(func.random())

        software = await session.execute(first_query)
        network = await session.execute(second_query)
        ai = await session.execute(third_query)

        software = ResultIntoList(result_proxy=software)
        network = ResultIntoList(result_proxy=network)
        ai = ResultIntoList(result_proxy=ai)

        result = list(itertools.chain(software.parse(), network.parse(), ai.parse()))

        num_random.shuffle(result)

        return result

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
