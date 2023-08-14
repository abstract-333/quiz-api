from fastapi import APIRouter, HTTPException
from fastapi_cache.decorator import cache
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from api.rating.rating_docs import SERVER_ERROR_UNAUTHORIZED_RESPONSE
from api.university.unviversity_service import UniversityService
from core.dependecies import UOWDep

university_router = APIRouter(
    prefix="/university",
    tags=["University"]
)


@cache(expire=3600 * 24)  # TTL = 3600 seconds * 24 = one hour * 24 = one day
@university_router.get("/get-all", name="university:get all", responses=SERVER_ERROR_UNAUTHORIZED_RESPONSE)
async def get_universities(
        request: Request,
        response: Response,
        uow: UOWDep,
):
    try:
        result = await UniversityService().get_universities(uow=uow)

        return {"status": "success",
                "data": result,
                "details": None
                }
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


