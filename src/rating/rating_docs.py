from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from starlette import status

from utilties.error_code import ErrorCode

GET_RATING_RESPONSE: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.OUT_OF_UNIVERSITY_ID: {
                    "summary": "Wrong entered university_id",
                    "value": {"detail": ErrorCode.OUT_OF_UNIVERSITY_ID},
                },
                }
            },
        },
    },
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
                }
                }
            },
        },
    },
}
SERVER_ERROR_UNAUTHORIZED_RESPONSE: OpenAPIResponseType = {
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
SERVER_ERROR_AUTHORIZED_RESPONSE: OpenAPIResponseType = {

    status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
    status.HTTP_403_FORBIDDEN: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.USER_NOT_AUTHENTICATED: {
                        "summary": "Not authenticated",
                        "value": {"detail": "Not authenticated"},
                    }
                }
            },
        },
    },
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

POST_RATING_RESPONSES.update(SERVER_ERROR_AUTHORIZED_RESPONSE)
GET_RATING_RESPONSE.update(SERVER_ERROR_AUTHORIZED_RESPONSE)
