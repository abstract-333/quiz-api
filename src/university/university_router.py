
from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from database import get_async_session
from rating.rating_docs import SERVER_ERROR_UNAUTHORIZED_RESPONSE
from university.university_db import get_universities_db

university_router = APIRouter(
    prefix="/university",
    tags=["University"]
)


@cache(expire=3600 * 24)  # TTL = 3600 seconds * 24 = one hour * 24 = one day
@university_router.get("/get-all", name="university:get all", responses=SERVER_ERROR_UNAUTHORIZED_RESPONSE)
async def get_universities(request: Request, response: Response, session: AsyncSession = Depends(get_async_session)):
    try:
        result = await get_universities_db(session=session)

        return {"status": "success",
                "data": result,
                "details": None
                }
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


