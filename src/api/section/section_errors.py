from typing import NamedTuple

from fastapi import HTTPException, status

from utilties.error_code import ErrorCode


class Errors(NamedTuple):
    invalid_section_400 = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorCode.OUT_OF_SECTION_ID
    )
    