from fastapi import Depends, Body, APIRouter, HTTPException
from fastapi_users import exceptions, BaseUserManager
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from pydantic import EmailStr
from starlette import status
from fastapi import Request
from auth.manager import get_user_manager
from auth.schemas import UserRead
from utils.error_code import ErrorCode

verify_router = APIRouter()

REQUEST_VERIFY_EMAIL_RESPONSE: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.USER_INACTIVE: {
                    "summary": "User is inactive.",
                    "value": {"detail": ErrorCode.USER_INACTIVE},
                }, ErrorCode.USER_NOT_EXISTS: {
                    "summary": "User not exists with this email.",
                    "value": {"detail": ErrorCode.USER_NOT_EXISTS},
                },
                    ErrorCode.VERIFY_USER_ALREADY_VERIFIED: {
                        "summary": "The user is already verified.",
                        "value": {
                            "detail": ErrorCode.VERIFY_USER_ALREADY_VERIFIED
                        },
                    },
                }
            }
        },
    }
}
VERIFY_EMAIL_RESPONSE: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.VERIFY_USER_BAD_TOKEN: {
                    "summary": "Invalid verify token or user with this email does not exists",
                    "value": {"detail": ErrorCode.VERIFY_USER_BAD_TOKEN},
                }
                    ,
                    ErrorCode.VERIFY_USER_ALREADY_VERIFIED: {
                        "summary": "The user is already verified.",
                        "value": {
                            "detail": ErrorCode.VERIFY_USER_ALREADY_VERIFIED
                        },
                    },
                }
            }
        },
    }
}


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
