from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from blacklist.blacklist_db import get_blacklist_user_db, get_blocked_level_db, update_blacklist_user_level_db
from blacklist.blacklist_schemas import BlacklistUpdate


async def raise_blocking_level(user_id: int, session: AsyncSession):
    """Raise the level of blocking or add new row if not exists"""
    blacklist_record = await get_blacklist_user_db(user_id=user_id, session=session)
    blocking_level = blacklist_record["blocking_level"] + 1
    if blacklist_record:
        # Check whether blocking level can be upper
        blocking_level_valid = await get_blocked_level_db(
            blocking_level=blocking_level,
            session=session
        )
        blocking_level_valid = blocking_level_valid["id"]

        if blocking_level_valid:
            await update_blacklist_user_level_db(
                user_id=user_id,
                blacklist_updated=BlacklistUpdate(blocking_level=blocking_level),
                session=session
            )

