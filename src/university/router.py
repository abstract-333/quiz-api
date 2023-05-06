from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from auth.base_config import current_user
from auth.models import university
from database import get_async_session
from utils.result_into_list import ResultIntoList

university_router = APIRouter(prefix="/university", tags=["University"])


@university_router.get("/get-all", name="university:get all", responses={
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal sever error.",
    },

})
@cache(expire=3600 * 24)  # TTL = 3600 seconds * 24 = one hour * 24 = one day
async def get_universities(session: AsyncSession = Depends(get_async_session), user=Depends(current_user)):
    try:
        query = select(university)
        result_proxy = await session.execute(query)
        result = ResultIntoList(result_proxy=result_proxy).parse()  # converting result to list
        return {"status": "success",
                "data": result,
                "details": None
                }
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "status": "error",
            "data": None,
            "details": Exception
        })
