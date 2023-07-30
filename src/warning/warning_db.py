import itertools

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from utilties.result_into_list import ResultIntoList
from warning.warning_models import warning
from warning.warning_schemas import WarningCreate, WarningUpdate


async def get_warning_db(
        user_id: int,
        session: AsyncSession
) -> warning:
    """Get user's warning record by user_id"""

    warning_query = select(warning).where(warning.c.user_id == user_id).limit(1)
    result_proxy = await session.execute(warning_query)

    result = ResultIntoList(result_proxy=result_proxy)
    result = list(itertools.chain(result.parse()))

    return result[0] if result else None


async def add_warning_db(
        warning_create: WarningCreate,
        session: AsyncSession
) -> None:
    """Add user to warning list"""

    stmt = insert(warning).values(**warning_create.model_dump())
    await session.execute(stmt)
    await session.commit()


async def update_warning_level_db(
        warning_updated: WarningUpdate,
        session: AsyncSession
) -> None:
    """Update level of warning user"""

    stmt = update(warning).values(**warning_updated.model_dump()).where(warning.c.user_id == warning_updated.user_id)
    await session.execute(stmt)
    await session.commit()


async def delete_warning_db(
        user_id: int,
        session: AsyncSession
) -> None:
    """Delete warning user's record from table"""

    stmt = delete(warning).where(warning.c.user_id == user_id)
    await session.execute(stmt)
    await session.commit()
