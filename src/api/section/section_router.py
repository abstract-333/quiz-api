from fastapi import APIRouter, HTTPException
from fastapi_cache.decorator import cache
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from api.rating.rating_docs import SERVER_ERROR_UNAUTHORIZED_RESPONSE
from api.section.section_service import SectionService
from core.dependecies import UOWDep

section_router = APIRouter(
    prefix="/section",
    tags=["Section"],
)


@cache(expire=3600 * 24)
@section_router.get("/get-all", name="section:section get-all",
                    responses=SERVER_ERROR_UNAUTHORIZED_RESPONSE)
async def get_sections(
        request: Request,
        response: Response,
        uow: UOWDep,
) -> dict:
    """Get all sections"""
    try:
        sections = await SectionService().get_sections(uow=uow)

        return {"status": "success",
                "data": sections,
                "details": None
                }
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
