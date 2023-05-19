import itertools
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from question.models import question
from question.schemas import QuestionRead
from utils.custom_exceptions import UserNotAdminSupervisor, NumberOfChoicesNotFour, AnswerNotIncluded
from utils.result_into_list import ResultIntoList


async def checking_question_validity(received_question: QuestionRead, role_id: int):

    received_question.choices.discard('')  # removing empty string from set

    if role_id == 1:  # user can't add questions
        raise UserNotAdminSupervisor

    if len(received_question.choices) != 4:  # checking if question have 4 choices
        raise NumberOfChoicesNotFour

    if received_question.answer not in received_question.choices:  # checking if answer included in choices
        raise AnswerNotIncluded


async def get_questions(page: int, user_id: int, session: AsyncSession):

    page -= 1
    page *= 10

    query = select(question).where(question.c.added_by == user_id).order_by(question.c.id).slice(page, page + 10)
    result_proxy = await session.execute(query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result


async def get_questions_section(page: int, section_id: int, session: AsyncSession):

    page -= 1
    page *= 10

    question_list_query = select(question).where(question.c.section_id == section_id).order_by(question.c.id) \
        .slice(page, page + 10)
    result_proxy = await session.execute(question_list_query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result


async def get_questions_title(question_title: str, session: AsyncSession):

    query = select(question).where(question.c.question_title == question_title)
    result_proxy = await session.execute(query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result

