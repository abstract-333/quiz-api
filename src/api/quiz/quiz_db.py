import itertools

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.question.question_models import question
from utilties.result_into_list import ResultIntoList


async def get_quiz_db(
        number_ai_questions: int,
        number_network_questions: int,
        number_software_questions: int,
        session: AsyncSession,
        user_id: int = None,
):
    """Get quiz and validate that quiz don't have questions that quiz taker write"""

    software_query = select(question).\
        filter(question.c.added_by != user_id, question.c.section_id == 1, question.c.active == 1).\
        order_by(func.random()).limit(number_software_questions)

    network_query = select(question).\
        filter(question.c.added_by != user_id, question.c.section_id == 2, question.c.active == 1).\
        order_by(func.random()).limit(number_network_questions)

    ai_query = select(question).\
        filter(question.c.added_by != user_id, question.c.section_id == 3, question.c.active == 1).\
        order_by(func.random()).limit(number_ai_questions)

    software = await session.execute(software_query)
    network = await session.execute(network_query)
    ai = await session.execute(ai_query)

    software = ResultIntoList(result_proxy=software)
    network = ResultIntoList(result_proxy=network)
    ai = ResultIntoList(result_proxy=ai)

    result = list(itertools.chain(software.parse(), network.parse(), ai.parse()))

    return result
