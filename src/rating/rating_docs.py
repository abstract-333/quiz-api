from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from starlette import status

from utils.error_code import ErrorCode


SERVER_ERROR_RESPONSE: OpenAPIResponseType = {
    status.HTTP_429_TOO_MANY_REQUESTS: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.TOO_MANY_REQUESTS: {
                    "summary": "Too many requests",
                    "value": {"detail": ErrorCode.TOO_MANY_REQUESTS},
                }}
            },
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal sever error.",
    }
}

POST_RATING_RESPONSES: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.QUESTIONS_NUMBER_INVALID: {
                        "summary": "Invalid number of questions",
                        "value": {"detail": ErrorCode.QUESTIONS_NUMBER_INVALID},
                    }
                }
            },
        },
    },
    status.HTTP_403_FORBIDDEN: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.ONLY_USER: {
                    "summary": "Only user can have rating",
                    "value": {"detail": ErrorCode.ONLY_USER},
                }, ErrorCode.USER_NOT_AUTHENTICATED: {
                    "summary": "Not authenticated",
                    "value": {"detail": "Not authenticated"},
                }
                }
            },
        },
    },
}

POST_RATING_RESPONSES.update(SERVER_ERROR_RESPONSE)