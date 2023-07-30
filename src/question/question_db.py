import itertools
from sqlalchemy import select, update, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from question.question_models import question
from question.question_schemas import QuestionUpdate, QuestionCreate
from utilties.result_into_list import ResultIntoList


async def get_questions_id_db(user_id: int, session: AsyncSession, page: int = 1):
    # get questions by user_id

    page -= 1
    page *= 10

    query = select(question).where(question.c.added_by == user_id).order_by(question.c.id).slice(page, page + 10)
    result_proxy = await session.execute(query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result


async def get_questions_section_db(show_inactive: False, page: int, section_id: int, session: AsyncSession):
    # get questions by section_id

    page -= 1
    page *= 10

    if not show_inactive:
        question_list_query = select(question). \
            filter(question.c.section_id == section_id, question.c.active == 1).order_by(question.c.id) \
            .slice(page, page + 10)
    else:
        question_list_query = select(question). \
            filter(question.c.section_id == section_id).order_by(question.c.id) \
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
    # Update question by question_id

    stmt = update(question).values(**question_update.model_dump()).where(question.c.id == question_id)
    await session.execute(stmt)
    await session.commit()


async def update_question_active_db(question_id: int, session: AsyncSession):
    # Update question by set active bool to False

    stmt = update(question).values(active=False).where(question.c.id == question_id)
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
    stmt = insert(question).values(**question_create.model_dump())
    await session.execute(stmt)
    await session.commit()


async def delete_question_db(question_id: int, session: AsyncSession):
    # delete question by id
    stmt = delete(question).where(question.c.id == question_id)
    await session.execute(stmt)
    await session.commit()


async def delete_all_questions_db(user_id: int, session: AsyncSession):
    """Delete all questions for user"""
    stmt = delete(question).where(question.c.added_by == user_id)
    await session.execute(stmt)
    await session.commit()


async def get_question_ref(list_questions: list, session: AsyncSession):
    # get references of questions by id
    query = select(question).where(question.c.id.in_(list_questions), question.c.reference_link != "")

    result_proxy = await session.execute(query)
    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result
