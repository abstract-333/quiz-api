from typing import NamedTuple

from fastapi import HTTPException, status

from utilties.error_code import ErrorCode


class Errors(NamedTuple):

    user_not_allowed_405 = HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail=ErrorCode.USER_NOT_ADMIN_SUPERVISOR
    )

    warns_user_400 = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorCode.WARNING_USER
    )

    temporary_blocked_400 = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorCode.TEMPORARY_BLOCKED
    )

    permanently_blocked_400 = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorCode.PERMANENTLY_BLOCKED
    )

    number_of_questions_invalid_400 = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorCode.QUESTIONS_NUMBER_INVALID
    )

    only_user_can_access_405 = HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail=ErrorCode.ONLY_USER
    )
