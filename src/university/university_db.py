import itertools

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth_models import university
from utilties.custom_exceptions import OutOfUniversityIdException
from utilties.result_into_list import ResultIntoList


async def get_universities_db(session: AsyncSession):
    """Get list of all universities"""

    query = select(university)
    result_proxy = await session.execute(query)
    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))  # converting result to list
    return result


async def get_university_id_db(university_id: int, session: AsyncSession):
    """Get university by id"""

    query = select(university).where(university.c.id == university_id)
    result_proxy = await session.execute(query)
    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))  # converting result to list
    return result


async def check_university_valid(university_id: int, session: AsyncSession):
    """Check whether university_id is valid"""

    university_get = await get_university_id_db(university_id=university_id, session=session)
    if university_get:
        raise OutOfUniversityIdException
