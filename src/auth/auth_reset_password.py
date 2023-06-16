from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi_users import exceptions, BaseUserManager
from pydantic import EmailStr
from starlette import status
from fastapi import Request

from auth.auth_docs import FORGET_PASSWORD_RESPONSES, RESET_PASSWORD_RESPONSES
from auth.auth_manager import get_user_manager
from utilties.error_code import ErrorCode

reset_password_router = APIRouter()


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
