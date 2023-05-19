import itertools

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from feedback.models import feedback
from utils.result_into_list import ResultIntoList


async def feedbacks_sent(page: int, session: AsyncSession, user_id: int):
    page -= 1
    page *= 10

    question_query = select(feedback).where(feedback.c.user_id == user_id).order_by(
        desc(feedback.c.added_at)).slice(page, page + 10)

    result_proxy = await session.execute(question_query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result


async def feedbacks_received(page: int, session: AsyncSession, user_id: int):
    page -= 1
    page *= 10

    question_query = select(feedback).where(feedback.c.question_author_id == user_id).order_by(
        desc(feedback.c.added_at)).slice(page, page + 10)
    result_proxy = await session.execute(question_query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result


async def feedbacks_by_id(feedback_id: int, session: AsyncSession):

    feedback_query = select(feedback).where(
        feedback.c.id == feedback_id).order_by(feedback.c.added_at)
    result_proxy = await session.execute(feedback_query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result
