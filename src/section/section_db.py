import itertools

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from section.section_models import section
from utilties.result_into_list import ResultIntoList


async def get_sections_db(session: AsyncSession):
    # get all sections
    query_section = select(section)

    result_proxy = await session.execute(query_section)
    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))  # converting result to list

    return result


async def get_sections_id_db(section_id: int, session: AsyncSession):
    # get section by id
    query_section = select(section).where(section.c.id == section_id)

    result_proxy = await session.execute(query_section)
    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))  # converting result to list

    return result
