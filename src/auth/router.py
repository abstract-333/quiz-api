from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from auth.base_config import fastapi_users, auth_backend
from auth.reset_password import reset_password_router
from auth.schemas import UserRead, UserCreate, UserUpdate
from auth.verify import verify_router

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
    fastapi_users.get_users_router(UserRead, UserUpdate),
    dependencies=[Depends(HTTPBearer())]
)

#
# @router.post("/login")
# async def login(data: ExtendedOAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_async_session),
#                 user_manager=Depends(get_user_manager)):
#     try:
#         returned_user = await user_manager.authenticate(credentials=data, session=session)
#         if returned_user is None:
#             raise exceptions.UserNotExists()
#         token = await get_jwt_strategy().write_token(returned_user)
#         return await bearer_transport.get_login_response(token=token, response=BearerResponse)
#     except exceptions.UserNotExists:
#         raise HTTPException(status_code=401, detail={
#             "status": "error",
#             "data": None,
#             "details": "User not exists, maybe you have entered wrong student_id or password"
#         })
#     except Exception:
#         raise HTTPException(status_code=500, detail={
#             "status": "error",
#             "data": None,
#             "details": Exception
#         })
