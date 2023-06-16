import itertools

from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from auth.auth_models import university
from database import get_async_session
from rating.rating_docs import SERVER_ERROR_RESPONSE
from utils.result_into_list import ResultIntoList

university_router = APIRouter(prefix="/university", tags=["University"])


@cache(expire=3600 * 24)  # TTL = 3600 seconds * 24 = one hour * 24 = one day
@university_router.get("/get-all", name="university:get all", responses=SERVER_ERROR_RESPONSE)
async def get_universities(request: Request, response: Response, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(university)
        result_proxy = await session.execute(query)
        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))  # converting result to list
        return {"status": "success",
                "data": result,
                "details": None
                }
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
