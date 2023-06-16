from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import Response
from database import get_async_session
from limiter import BucketLimiter
from rating.rating_docs import SERVER_ERROR_RESPONSE
from section.section_db import get_sections_db

section_router = APIRouter(
    prefix="/section",
    tags=["Section"],
    dependencies=[Depends(BucketLimiter())]
)


@cache(expire=100)
@section_router.get("/get-all", name="section:section get-all",
                    responses=SERVER_ERROR_RESPONSE)
async def get_sections(request: Request, response: Response,
                       session: AsyncSession = Depends(get_async_session)) -> dict:
    """get all sections"""
    try:
        sections = await get_sections_db(session=session)

        return {"status": "success",
                "data": sections,
                "details": None
                }
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
