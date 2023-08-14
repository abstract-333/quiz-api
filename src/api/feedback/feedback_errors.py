from typing import NamedTuple

from fastapi import HTTPException, status

from utilties.error_code import ErrorCode


class Errors(NamedTuple):
    rating_mark_400 = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorCode.RATING_EXCEPTION
    )

    question_not_exists_404 = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=ErrorCode.QUESTION_NOT_FOUND
    )

    not_allowed_405 = HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail=ErrorCode.NOT_ALLOWED_FEEDBACK_YOURSELF
    )

    feedback_duplicated_title_409 = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=ErrorCode.DUPLICATED_TITLE
    )

    invalid_page_number_400 = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorCode.INVALID_PAGE
    )

    user_not_allowed_405 = HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail=ErrorCode.USER_NOT_ADMIN_SUPERVISOR
    )

    feedback_not_found_404 = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=ErrorCode.FEEDBACK_NOT_FOUND
    )

    not_allowed_editing_405 = HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail=ErrorCode.NOT_ALLOWED_PATCH_FEEDBACK
    )

    time_editing_elapsed_405 = HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="You can edit the feedback for 15 minutes after you sent it"
    )

    not_allowed_feedback_yourself_405 = HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail=ErrorCode.NOT_ALLOWED_FEEDBACK_YOURSELF
    )
