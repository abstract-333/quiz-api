from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from database import get_async_session
from section.models import section
from fastapi_cache.decorator import cache
from utils.result_into_list import ResultIntoList

section_router = APIRouter(
    prefix="/section",
    tags=["Section"],
)


@section_router.get("/get-all", name="section:section get-all", dependencies=[Depends(HTTPBearer())], responses={
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal sever error.",
    },

})
@cache(expire=3600 * 24)
async def add_quiz(session: AsyncSession = Depends(get_async_session)) -> dict:
    try:
        query = select(section)
        result_proxy = await session.execute(query)
        result = ResultIntoList(result_proxy=result_proxy).parse()  # converting result to list
        return {"status": "success",
                "data": result,
                "details": None
                }
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "status": "error",
            "details": Exception
        })