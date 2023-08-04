import itertools

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.auth.auth_docs import SEARCH_USER_RESPONSE
from api.auth.auth_models import User, user
from api.auth.base_config import current_superuser
from database import get_async_session
from utilties.custom_exceptions import InvalidPage
from utilties.error_code import ErrorCode
from utilties.result_into_list import ResultIntoList

search_users_router = APIRouter(
    prefix="/search",
)


@search_users_router.get(
    path="",
    name="user:get user by name or email",
    dependencies=[Depends(HTTPBearer())],
    responses=SEARCH_USER_RESPONSE
)
async def get_users(
        page: int = 1,
        username: str = '',
        email: str = '',
        verified_superuser: User = Depends(current_superuser),
        session: AsyncSession = Depends(get_async_session)
):
    """Get users by username, email or both"""
    try:
        # Validate that entered page is not below 1
        if page < 1:
            raise InvalidPage

        page -= 1
        page *= 10

        query = select(
            user.c.id,
            user.c.username,
            user.c.email,
            user.c.role_id,
            user.c.university_id,
            user.c.phone,
            user.c.section_id,
            user.c.registered_at,
            user.c.is_active,
            user.c.is_superuser,
            user.c.is_verified,)\
            .filter(
            user.c.id != verified_superuser.id,
            user.c.username.like(f"%{username}%"),
            user.c.email.like(f"%{email}%")).\
            slice(page, page + 10)
        result_proxy = await session.execute(query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        return {"status": "success",
                "data": result,
                "detail": None
                }

    except InvalidPage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.INVALID_PAGE)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
