from fastapi import Depends, Body, APIRouter, HTTPException
from fastapi import Request
from fastapi_users import exceptions, BaseUserManager
from pydantic import EmailStr
from starlette import status

from api.auth.auth_docs import REQUEST_VERIFY_EMAIL_RESPONSE, VERIFY_EMAIL_RESPONSE
from api.auth.auth_manager import get_user_manager
from api.auth.auth_schemas import UserRead
from utilties.error_code import ErrorCode

verify_router = APIRouter()


@verify_router.post(
    "/request-verify-token",
    status_code=status.HTTP_202_ACCEPTED,
    name="verify:request-token",
    responses=REQUEST_VERIFY_EMAIL_RESPONSE
)
async def request_verify_token(
        request: Request,
        email: EmailStr = Body(..., embed=True),
        user_manager: BaseUserManager = Depends(get_user_manager),
):
    try:
        user = await user_manager.get_by_email(email)
        await user_manager.request_verify(user, request)
        return {
            "status": 202,
            "data": None,
            "details": "Verification token sent successfully to your email"
        }
    except exceptions.UserNotExists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.USER_NOT_EXISTS)
    except exceptions.UserInactive:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.USER_INACTIVE)
    except exceptions.UserAlreadyVerified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED)


@verify_router.get(
    "/verify",
    response_model=UserRead,
    name="verify:verify",
    responses=VERIFY_EMAIL_RESPONSE
)
async def verify(
        request: Request,
        token: str,
        user_manager=Depends(get_user_manager)):
    try:
        return await user_manager.verify(token, request)
    except (exceptions.InvalidVerifyToken, exceptions.UserNotExists):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.VERIFY_USER_BAD_TOKEN)
    except exceptions.UserAlreadyVerified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED)
