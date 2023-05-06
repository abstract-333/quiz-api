from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi_users import exceptions, BaseUserManager
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from pydantic import EmailStr
from starlette import status
from fastapi import Request
from auth.manager import get_user_manager
from utils.error_code import ErrorCode

reset_password_router = APIRouter()

FORGET_PASSWORD_RESPONSES: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.USER_NOT_EXISTS: {
                    "summary": "User not exists with this email",
                    "value": {"detail": ErrorCode.USER_NOT_EXISTS},
                }, ErrorCode.USER_INACTIVE: {
                    "summary": "User inactive",
                    "value": {"detail": ErrorCode.USER_INACTIVE},
                },
                }
            }
        },
    },
}

RESET_PASSWORD_RESPONSES: OpenAPIResponseType = {status.HTTP_400_BAD_REQUEST: {
    "model": ErrorModel,
    "content": {
        "application/json": {
            "examples": {ErrorCode.USER_INACTIVE: {
                "summary": "Bad or expired token.",
                "value": {"detail": ErrorCode.USER_INACTIVE},
            }, ErrorCode.USER_NOT_EXISTS: {
                "summary": "Bad or expired token.",
                "value": {"detail": ErrorCode.USER_NOT_EXISTS},
            },
                ErrorCode.RESET_PASSWORD_BAD_TOKEN: {
                    "summary": "Bad or expired token.",
                    "value": {"detail": ErrorCode.RESET_PASSWORD_BAD_TOKEN},
                },
                ErrorCode.RESET_PASSWORD_INVALID_PASSWORD: {
                    "summary": "Password validation failed.",
                    "value": {
                        "detail": {
                            "code": ErrorCode.RESET_PASSWORD_INVALID_PASSWORD,
                            "reason": "Password should be at least 8 characters",
                        }
                    },
                },
            }
        }
    },
}
}


@reset_password_router.post(
    "/forgot-password",
    status_code=status.HTTP_202_ACCEPTED,
    name="reset:forgot_password",
    responses=FORGET_PASSWORD_RESPONSES

)
async def forgot_password(
        request: Request,
        email: EmailStr = Body(..., embed=True),
        user_manager: BaseUserManager = Depends(get_user_manager)
):
    try:
        user = await user_manager.get_by_email(email)
    except exceptions.UserNotExists:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.USER_NOT_EXISTS)

    try:
        await user_manager.forgot_password(user, request)
        return {
            "status": 202,
            "data": None,
            "details": "Password reset token sent successfully to your email"
        }
    except exceptions.UserInactive:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.USER_INACTIVE)


@reset_password_router.post(
    "/reset-password",
    name="reset:reset_password",
    responses=RESET_PASSWORD_RESPONSES
)
async def reset_password(
        request: Request,
        token: str = Body(...),
        password: str = Body(...),
        user_manager: BaseUserManager = Depends(get_user_manager)
):
    try:
        await user_manager.reset_password(token, password, request)
        return {
            "status": 200,
            "data": None,
            "details": "Password reset successfully"
        }

    except (
            exceptions.InvalidResetPasswordToken,
            exceptions.UserNotExists,
            exceptions.UserInactive,
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN)
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(status_code=400, detail={
            "status": "error",
            "data": None,
            "details": e.reason
        }
                            )