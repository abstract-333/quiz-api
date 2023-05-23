import itertools
from datetime import datetime

from sqlalchemy import select, desc, delete, TIMESTAMP
from sqlalchemy.ext.asyncio import AsyncSession

from feedback.feedback_models import feedback
from question.question_models import question
from utils.result_into_list import ResultIntoList


async def get_remaining_time(added_time: TIMESTAMP, target_time):
    # return remaining turn until targeting time will be elapsed
    remaining_time = (datetime.utcnow() - added_time).seconds
    remaining_time = target_time - remaining_time

    return remaining_time


async def feedback_sent_db(page: int, session: AsyncSession, user_id: int):
    # get feedbacks that user send with pagination
    page -= 1
    page *= 10

    question_query = select(feedback, question.c.question_title).where(feedback.c.user_id == user_id). \
        join(question, feedback.c.question_id == question.c.id and
             feedback.c.user_id == user_id).order_by(
        desc(feedback.c.added_at)).slice(page, page + 10)

    result_proxy = await session.execute(question_query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result


async def feedback_received_db(page: int, session: AsyncSession, user_id: int):
    # get feedbacks that supervisor/admin receive with pagination

    page -= 1
    page *= 10

    question_query = select(feedback, question.c.question_title).join(question, feedback.c.question_id == question.c.id
                                                                      and feedback.c.question_author_id == user_id). \
        order_by(desc(feedback.c.added_at)).slice(page, page + 10)
    result_proxy = await session.execute(question_query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result


async def feedback_by_id_db(feedback_id: int, session: AsyncSession):
    # get feedbacks by user_id

    feedback_query = select(feedback).where(
        feedback.c.id == feedback_id).order_by(feedback.c.added_at)
    result_proxy = await session.execute(feedback_query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result


async def feedback_question_id_user_id_db(question_id: int, user_id: int, session: AsyncSession):
    # get feedbacks by user_id and question_id

    feedback_query = select(feedback).where(
        feedback.c.question_id == question_id and feedback.c.user_id == user_id).order_by(
        feedback.c.added_at)
    result_proxy = await session.execute(feedback_query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result


async def check_feedback_question_id(question_id: int, session: AsyncSession):
    # check if question has feedback

    feedback_query = select(feedback).where(
        feedback.c.question_id == question_id).limit(1)
    result_proxy = await session.execute(feedback_query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result


async def delete_feedback_question_id(question_id: int, session: AsyncSession):
    # delete feedback for specific question

    stmt = delete(feedback).where(feedback.c.question_id == question_id)
    await session.execute(stmt)
    await session.commit()


async def delete_feedback_id(feedback_id: int, session: AsyncSession):
    # delete feedback by feedback_id

    stmt = delete(feedback).where(feedback.c.id == feedback_id)
    await session.execute(stmt)
    await session.commit()
