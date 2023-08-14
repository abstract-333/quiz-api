from sqlalchemy.ext.asyncio import AsyncSession

from api.blacklist.blacklist_db import add_blacklist_user_db
from api.blacklist.blacklist_schemas import BlacklistCreate
from api.warning.warning_db import get_warning_db, delete_warning_db, update_warning_level_db, add_warning_db
from api.warning.warning_schemas import WarningUpdate, WarningCreate
from utilties.custom_exceptions import AddedToBlacklist, WarnsUserException


async def manage_warning_level(user_id: int, session: AsyncSession):
    """Raise the level of warning or add new row if not exists"""

    warning_record = await get_warning_db(user_id=user_id, session=session)

    # Check if warning record exist
    if warning_record:
        warning_level = warning_record["warning_level"]
        # Check whether warning record exists and can be upper
        if warning_level == 3:
            # If warning_level equal to 3 then delete record from warning table
            # and add new record to blocked table
            blacklist_record = BlacklistCreate(user_id=user_id)
            await add_blacklist_user_db(blacklist_create=blacklist_record, session=session)

            await delete_warning_db(user_id=user_id, session=session)

            raise AddedToBlacklist

        elif warning_level in (1, 2):
            # Update warning record for user if not have maximum warning level
            updated_warning = WarningUpdate(user_id=user_id, warning_level=warning_level+1)

            await update_warning_level_db(
                warning_updated=updated_warning,
                session=session
            )

            raise WarnsUserException
        else:
            # Update warning to default value 1 if something went wrong
            updated_warning = WarningUpdate(user_id=user_id, warning_level=1)

            await update_warning_level_db(
                warning_updated=updated_warning,
                session=session
            )

            raise WarnsUserException
    else:
        # Add new warning record because no record for this user exists
        warning_create = WarningCreate(user_id=user_id)
        await add_warning_db(warning_create=warning_create, session=session)

        raise WarnsUserException


