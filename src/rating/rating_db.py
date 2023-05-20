import itertools

from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from rating.models import rating
from rating.schemas import RatingUpdate, RatingCreate
from utils.result_into_list import ResultIntoList


async def get_rating_user_id(user_id: int, session: AsyncSession):
    # get rating by user_id

    query = select(rating).where(rating.c.user_id == user_id)
    result_proxy = await session.execute(query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result


async def update_rating_db(rating_id: int, updated_rating: RatingUpdate, session: AsyncSession):
    # update rating

    stmt = update(rating).values(**updated_rating.dict()).where(rating.c.id == rating_id)
    await session.execute(stmt)
    await session.commit()


async def insert_rating_db(rating_create: RatingCreate, session: AsyncSession):
    # insert rating
    stmt = insert(rating).values(**rating_create.dict())
    await session.execute(stmt)
    await session.commit()