import itertools

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import user
from rating.models import rating
from utils.result_into_list import ResultIntoList


async def rating_user_id(user_id: int, session: AsyncSession):

    query = select(rating).where(rating.c.user_id == user_id)
    result_proxy = await session.execute(query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result