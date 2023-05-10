from fastapi import HTTPException
from starlette import status


class DuplicatedQuizException(Exception):
    """Quiz duplicated"""
    pass


class UserNotAdminSupervisor(Exception):
    """USER_NOT_ADMIN_SUPERVISOR"""
    pass


USER_NOT_EXISTS_HTTP_EXCEPTION = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={
    "status": "error",
    "data": None,
    "detail": "User not exists, you have entered wrong Email"
})
USER_INACTIVE_HTTP_EXCEPTION = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={
    "status": "error",
    "data": None,
    "detail": "User is inactive"
})
USER_ALREADY_VERIFIED_HTTP_EXCEPTION = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={
    "status": "error",
    "data": None,
    "detail": "User already verified"
})
USER_VERIFY_BAD_TOKEN_HTTP_EXCEPTION = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={
    "status": "error",
    "data": None,
    "detail": "verify bad token"
}
                                                     )
USER_RESET_PASSWORD_BAD_TOKEN_HTTP_EXCEPTION = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={
    "status": "error",
    "data": None,
    "detail": "reset password bad token"
}
                                                             )
SERVER_ERROR_500 = HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
    "status": "error",
    "data": None,
    "detail": Exception
})
