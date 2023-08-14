from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from api.auth.auth_patch import manage_users_router
from api.auth.auth_reset_password import reset_password_router
from api.auth.auth_schemas import UserRead, UserCreate
from api.auth.auth_verify import verify_router
from api.auth.base_config import fastapi_users, auth_backend
from api.auth.get_users import search_users_router

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend, requires_verification=True),
)
auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)
auth_router.include_router(verify_router)
auth_router.include_router(reset_password_router)
auth_router.include_router(
    search_users_router,
    dependencies=[Depends(HTTPBearer())]
)
auth_router.include_router(
    manage_users_router,
    dependencies=[Depends(HTTPBearer())]
)
