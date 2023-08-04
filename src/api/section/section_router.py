from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from starlette import status
from starlette.requests import Request
from starlette.responses import Response
from api.rating.rating_docs import SERVER_ERROR_UNAUTHORIZED_RESPONSE
from api.section.section_service import SectionService
from api.section.section_depedency import section_service_dependency

section_router = APIRouter(
    prefix="/section",
    tags=["Section"],
)


@cache(expire=100)
@section_router.get("/get-all", name="section:section get-all",
                    responses=SERVER_ERROR_UNAUTHORIZED_RESPONSE)
async def get_sections(
        request: Request,
        response: Response,
        section_service: Annotated[SectionService, Depends(section_service_dependency)],
) -> dict:
    """Get all sections"""
    try:
        sections = await section_service.get_sections()

        return {"status": "success",
                "data": sections,
                "details": None
                }
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
