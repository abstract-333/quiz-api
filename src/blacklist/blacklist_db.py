import itertools

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from blacklist.blacklist_models import blacklist, blocked_level

from blacklist.blacklist_schemas import BlacklistCreate, BlacklistUpdate
from utilties.result_into_list import ResultIntoList


async def get_blacklist_user_db(user_id: int, session: AsyncSession):
    """Get user's blacklist record by user_id"""

    blacklist_query = select(blacklist).where(blacklist.c.user_id == user_id).limit(1)
    result_proxy = await session.execute(blacklist_query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result[0] if result else None


async def add_blacklist_user_db(blacklist_create: BlacklistCreate, session: AsyncSession):
    """Add user to blacklist"""

    stmt = insert(blacklist).values(**blacklist_create.model_dump())
    await session.execute(stmt)
    await session.commit()


async def update_blacklist_user_level_db(blacklist_updated: BlacklistUpdate, user_id: int, session: AsyncSession):
    """Raise level of blocked user"""

    stmt = update(blacklist).values(**blacklist_updated.model_dump()).where(blacklist.c.user_id == user_id)
    await session.execute(stmt)
    await session.commit()


async def delete_blacklist_db(user_id: int, session: AsyncSession):
    """Delete blocked user record from table"""

    stmt = delete(blacklist).where(blacklist.c.user_id == user_id)
    await session.execute(stmt)
    await session.commit()


async def get_blocked_level_db(blocking_level: int, session: AsyncSession):
    """Get blocking level record"""

    query = select(blocked_level).where(blocked_level.c.id == blocking_level)
    result_proxy = await session.execute(query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result[0] if result else None


async def get_unblocked_after_db(user_id: int, session: AsyncSession):
    """Get unblocked after"""

    query = select(blacklist.c.blocked_at, blocked_level.c.unblocked_after).\
        join(blocked_level, blocked_level.c.id == blacklist.c.blocking_level).filter(blacklist.c.user_id == user_id)

    result_proxy = await session.execute(query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))
    return result[0] if result else None
