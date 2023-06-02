from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from starlette import status

from rating.rating_docs import SERVER_ERROR_RESPONSE
from utils.error_code import ErrorCode

GET_QUIZ_RESPONSES: OpenAPIResponseType = {
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
                "examples": {ErrorCode.USER_NOT_AUTHENTICATED: {
                    "summary": "Not authenticated",
                    "value": {"detail": "Not authenticated"},
                }}
            },
        },
    },

}

GET_QUIZ_RESPONSES.update(SERVER_ERROR_RESPONSE)
