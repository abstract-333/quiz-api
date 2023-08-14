from typing import NamedTuple

from fastapi import HTTPException, status

from utilties.error_code import ErrorCode


class Errors(NamedTuple):

    number_choices_not_four_400 = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorCode.NUMBER_OF_CHOICES_NOT_FOUR
    )

    answer_not_included_choices_400 = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorCode.ANSWER_NOT_INCLUDED_IN_CHOICES
    )

    user_not_allowed_405 = HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail=ErrorCode.USER_NOT_ADMIN_SUPERVISOR
    )

    duplicated_question_409 = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=ErrorCode.QUESTION_DUPLICATED
    )

    invalid_page_number_400 = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorCode.INVALID_PAGE
    )

    question_not_found_404 = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=ErrorCode.QUESTION_NOT_FOUND
    )

    not_question_owner_405 = HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail=ErrorCode.NOT_QUESTION_OWNER
    )

    question_not_editable_405 = HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="You can edit the question for 30 minutes after you sent it"
    )
