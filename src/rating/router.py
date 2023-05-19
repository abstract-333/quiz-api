import itertools

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth.models import user
from database import get_async_session
from feedback.models import feedback
from utils.result_into_list import ResultIntoList

rating_router = APIRouter(
    prefix="/rating",
    tags=["Rating"],
)


@rating_router.get("/supervisor", name="supervisor:get best rating")
async def add_feedback(session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(
            user.c.username,
            (func.sum(feedback.c.rating) / func.count(feedback.c.id)).label('average_rating'),
            func.count(feedback.c.id).label('count_of_rates')
        ).join(feedback, user.c.id == feedback.c.question_author_id).\
            order_by(desc((func.sum(feedback.c.rating) / func.count(feedback.c.id))))\
            .group_by(feedback.c.question_author_id). \
            having((func.sum(feedback.c.rating) / func.count(feedback.c.id)) > 2.5). \
            limit(10)

        result_proxy = await session.execute(query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        return result
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


