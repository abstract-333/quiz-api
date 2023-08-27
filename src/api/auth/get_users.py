import itertools

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from sqlalchemy import select
from starlette import status

from api.auth.auth_docs import SEARCH_USER_RESPONSE
from api.auth.auth_models import user
from api.auth.auth_schemas import UserRead
from core.dependecies import CurrentSuperUser, Session
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
        verified_superuser: CurrentSuperUser,
        session: Session,
        page: int = Query(gt=0, default=1),
        username: str = '',
        email: str = '',
):
    """Get users by username, email or both"""
    try:
        # Validate that entered page is not below 1
        if page < 1:
            raise InvalidPage

        page -= 1
        page *= 10

        query = select(UserRead)\
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
