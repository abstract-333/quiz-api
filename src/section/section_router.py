import itertools
from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from fastapi_limiter.depends import RateLimiter
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from database import get_async_session
from rating.rating_docs import SERVER_ERROR_RESPONSE
from section.section_models import section
from utils.result_into_list import ResultIntoList

section_router = APIRouter(
    prefix="/section",
    tags=["Section"],
)


@cache(expire=100)
@section_router.get("/get-all", name="section:section get-all", responses=SERVER_ERROR_RESPONSE)
async def get_sections(request: Request, response: Response,
                       session: AsyncSession = Depends(get_async_session)) -> dict:
    try:
        query = select(section)
        result_proxy = await session.execute(query)
        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))  # converting result to list
        return {"status": "success",
                "data": result,
                "details": None
                }
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
