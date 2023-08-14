from typing import NamedTuple

from fastapi import HTTPException, status

from utilties.error_code import ErrorCode


class Errors(NamedTuple):
    empty_list_returned_404 = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=ErrorCode.EMPTY_LIST
    )

    number_of_requested_questions_invalid_400 = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorCode.EMPTY_LIST
    )
