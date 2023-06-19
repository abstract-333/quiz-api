from math import ceil

from fastapi import HTTPException
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from utilties.error_code import ErrorCode


async def default_callback(request: Request, response: Response, pexpire: int):

    expire = ceil(pexpire / 1000)
    expire = str(expire)

    raise HTTPException(
        status.HTTP_429_TOO_MANY_REQUESTS, detail=ErrorCode.TOO_MANY_REQUESTS, headers={"Retry-After": expire}
    )
