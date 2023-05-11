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
    status.HTTP_404_NOT_FOUND: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {"USER_INACTIVE_OR_NOT_EXISTS": {
                    "summary": "User inactive or not exists",
                    "value": {"detail": "USER_INACTIVE_OR_NOT_EXISTS"},
                },
                }
            }
        },
    },
}

RESET_PASSWORD_RESPONSES: OpenAPIResponseType = {status.HTTP_401_UNAUTHORIZED: {
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
                    "summary": "Password validation failed."
                    ,
                    "value": {
                        "detail": ("Password should be at least 8 characters",
                                   "Password should not contain email",
                                   "Password must contain at least one uppercase letter",
                                   "Password must contain at least one lowercase letter",
                                   "Password must contain at least one digit",
                                   "Password must contain at least one special character",
                                   ),
                    },
                },
            }
        }
    },
}
}


@reset_password_router.post(
    "/forgot-password",
    name="reset:forgot_password",
    status_code=202,
    responses=FORGET_PASSWORD_RESPONSES

)
async def forgot_password(
        request: Request,

        email: EmailStr = Body(..., embed=True),
        user_manager: BaseUserManager = Depends(get_user_manager)
):
    try:
        user = await user_manager.get_by_email(email)
        await user_manager.forgot_password(user, request)
        return {
            "status": "success",
            "data": None,
            "detail": "Password reset token sent successfully to your email"
        }
    except (exceptions.UserInactive, exceptions.UserNotExists):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorCode.USER_INACTIVE_OR_NOT_EXISTS)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


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
            "status": "success",
            "data": None,
            "details": "Password reset successfully"
        }
    except (
            exceptions.InvalidResetPasswordToken,
            exceptions.UserNotExists,
            exceptions.UserInactive,
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN)
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(status_code=400, detail=e.reason)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
