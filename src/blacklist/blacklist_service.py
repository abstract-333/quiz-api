from datetime import datetime

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth_models import User
from auth.base_config import current_user
from blacklist.blacklist_db import get_blacklist_user_db, get_blocked_level_db, update_blacklist_user_level_db, \
    get_unblocked_after_db
from blacklist.blacklist_schemas import BlacklistUpdate
from database import get_async_session
from utilties.custom_exceptions import RaisingBlockingLevel, HighestBlockingLevel, BlockedReturnAfter


async def manage_blocking_level(
        user_id: int,
        session: AsyncSession
) -> None:
    """Raise the level of blocking or add new row if not exists"""
    blocking_level = await get_blocking_level(user_id=user_id, session=session)
    new_level = blocking_level + 1

    if blocking_level:
        # Check whether blocking level can be upper
        blocking_level_valid = await get_blocked_level_db(
            blocking_level=new_level,
            session=session
        )

        if blocking_level_valid:
            await update_blacklist_user_level_db(
                user_id=user_id,
                blacklist_updated=BlacklistUpdate(blocking_level=new_level),
                session=session
            )

            if blocking_level_valid["unblocked_after"] == -1:
                raise HighestBlockingLevel

            else:
                raise RaisingBlockingLevel

        else:
            raise HighestBlockingLevel


async def get_blocking_level(
        user_id: int,
        session: AsyncSession
) -> int | None:
    """Get blocking level for the use by user_id"""
    blacklist_record = await get_blacklist_user_db(user_id=user_id, session=session)

    if blacklist_record:
        return blacklist_record["blocking_level"]

    return None


async def get_unblocked_after(
        user_id: int,
        session: AsyncSession
):
    """When the user will be unblocked"""
    unblocked_after = await get_unblocked_after_db(user_id=user_id, session=session)

    return unblocked_after


async def get_blocking_time(
        user_id: int,
        session: AsyncSession
) -> int | None:
    """Time remaining to unblock user if he is blocked"""

    blocking_record = await get_unblocked_after(user_id=user_id, session=session)
    if blocking_record:

        blocked_at = blocking_record["blocked_at"]
        unblocked_after = blocking_record["unblocked_after"]

        # Check if permanently blocked
        if unblocked_after == -1:
            raise HighestBlockingLevel

        # Calculate remaining time until user will be unblocked
        remaining_time = (datetime.utcnow() - blocked_at).days
        remaining_time = unblocked_after - remaining_time

        return remaining_time if remaining_time >= 0 else None

