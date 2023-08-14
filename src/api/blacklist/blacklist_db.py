import itertools

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from api.blacklist.blacklist_models import Blacklist, BlockedLevel
from api.blacklist.blacklist_schemas import BlacklistCreate, BlacklistUpdate
from utilties.result_into_list import ResultIntoList


async def get_blacklist_user_db(user_id: int, session: AsyncSession):
    """Get user's blacklist record by user_id"""

    blacklist_query = select(Blacklist).where(Blacklist.user_id == user_id).limit(1)
    result_proxy = await session.execute(blacklist_query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result[0] if result else None


async def add_blacklist_user_db(blacklist_create: BlacklistCreate, session: AsyncSession):
    """Add user to blacklist"""

    stmt = insert(Blacklist).values(**blacklist_create.model_dump())
    await session.execute(stmt)
    await session.commit()


async def update_blacklist_user_level_db(blacklist_updated: BlacklistUpdate, user_id: int, session: AsyncSession):
    """Raise level of blocked user"""

    stmt = update(Blacklist).values(**blacklist_updated.model_dump()).where(Blacklist.user_id == user_id)
    await session.execute(stmt)
    await session.commit()


async def delete_blacklist_db(user_id: int, session: AsyncSession):
    """Delete blocked user record from table"""

    stmt = delete(Blacklist).where(Blacklist.user_id == user_id)
    await session.execute(stmt)
    await session.commit()


async def get_blocked_level_db(blocking_level: int, session: AsyncSession):
    """Get blocking level record"""

    blocking_level_record = await session.get(BlockedLevel, blocking_level)

    return blocking_level_record


async def get_unblocked_after_db(user_id: int, session: AsyncSession):
    """Get unblocked after"""
    query = select(Blacklist.blocked_at, BlockedLevel.unblocked_after). \
        join(BlockedLevel).filter(Blacklist.user_id == user_id)
    result_proxy = await session.execute(query)
    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))
    return result[0] if result else None
