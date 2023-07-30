import itertools

from sqlalchemy import select, update, insert, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession
from rating.rating_models import rating
from rating.rating_schemas import RatingUpdate, RatingCreate
from utilties.result_into_list import ResultIntoList


async def get_rating_user_id(user_id: int, session: AsyncSession):
    # get rating by user_id

    query = select(rating).where(rating.c.user_id == user_id).order_by(desc(rating.c.added_at)).limit(7)
    result_proxy = await session.execute(query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result


async def get_last_rating_user(user_id: int, session: AsyncSession):
    # get rating by user_id

    query = select(rating).where(rating.c.user_id == user_id).order_by(desc(rating.c.added_at)).limit(1)
    result_proxy = await session.execute(query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result


async def update_rating_db(rating_id: int, updated_rating: RatingUpdate, session: AsyncSession):
    # update rating

    stmt = update(rating).values(**updated_rating.model_dump()).where(rating.c.id == rating_id)
    await session.execute(stmt)
    await session.commit()


async def insert_rating_db(rating_create: RatingCreate, session: AsyncSession):
    # insert rating
    stmt = insert(rating).values(**rating_create.model_dump())
    await session.execute(stmt)
    await session.commit()


async def delete_rating_db(user_id: int, session: AsyncSession):
    """Delete all rating records for user"""
    stmt = delete(rating).where(rating.c.user_id == user_id)
    await session.execute(stmt)
    await session.commit()
