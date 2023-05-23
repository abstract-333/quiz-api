import itertools
from sqlalchemy import select, update, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from question.models import question
from question.schemas import QuestionRead, QuestionUpdate, QuestionCreate
from utils.custom_exceptions import UserNotAdminSupervisor, NumberOfChoicesNotFour, AnswerNotIncluded
from utils.result_into_list import ResultIntoList


async def check_question_validity(received_question: QuestionRead, role_id: int):
    received_question.choices.discard('')  # removing empty string from set

    if role_id == 1:  # user can't add questions
        raise UserNotAdminSupervisor

    if len(received_question.choices) != 4:  # checking if question have 4 choices
        raise NumberOfChoicesNotFour

    if received_question.answer not in received_question.choices:  # checking if answer included in choices
        raise AnswerNotIncluded


async def get_questions_id_db(page: int, user_id: int, session: AsyncSession):
    # get questions by user_id

    page -= 1
    page *= 10

    query = select(question).where(question.c.added_by == user_id).order_by(question.c.id).slice(page, page + 10)
    result_proxy = await session.execute(query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result


async def get_questions_section_db(page: int, section_id: int, session: AsyncSession):
    # get questions by section_id

    page -= 1
    page *= 10

    question_list_query = select(question).where(question.c.section_id == section_id).order_by(question.c.id) \
        .slice(page, page + 10)
    result_proxy = await session.execute(question_list_query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result


async def get_questions_title_db(question_title: str, session: AsyncSession):
    # get questions by question_title

    query = select(question).where(question.c.question_title == question_title)
    result_proxy = await session.execute(query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result


async def get_question_id_db(question_id: int, session: AsyncSession):
    # get questions by id
    question_query = select(question).where(
        question.c.id == question_id)
    result_proxy = await session.execute(question_query)

    result_question = ResultIntoList(result_proxy=result_proxy)
    result_question = list(itertools.chain(result_question.parse()))

    return result_question


async def update_question_db(question_id: int, question_update: QuestionUpdate, session: AsyncSession):
    # get question by question_id

    stmt = update(question).values(**question_update.dict()).where(question.c.id == question_id)
    await session.execute(stmt)
    await session.commit()


async def get_questions_duplicated_db(question_title: str, question_id: int, session: AsyncSession):
    # get duplicated questions

    query = select(question).where(question.c.question_title == question_title and
                                   question.c.id != question_id)
    result_proxy = await session.execute(query)
    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))
    return result


async def insert_question_db(question_create: QuestionCreate, session: AsyncSession):
    stmt = insert(question).values(**question_create.dict())
    await session.execute(stmt)
    await session.commit()


async def delete_question_db(question_id: int, session: AsyncSession):
    # delete question by id
    stmt = delete(question).where(question.c.id == question_id)
    await session.execute(stmt)
    await session.commit()

