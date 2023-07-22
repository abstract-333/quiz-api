import itertools

from sqlalchemy import select

from auth.auth_models import user
from database import async_session_maker
from utilties.result_into_list import ResultIntoList


async def get_user_db(email):
    # Get user by email
    async with async_session_maker() as session:
        user_query = select(user).where(user.c.email == email)
        result_proxy = await session.execute(user_query)

        user_new = ResultIntoList(result_proxy=result_proxy)
        user_new = list(itertools.chain(user_new.parse()))

        return user_new[0] if user_new else None
