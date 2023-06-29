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
GET_RATING_SUPERVISOR_RESPONSE: OpenAPIResponseType = {
    status.HTTP_405_METHOD_NOT_ALLOWED: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.USER_NOT_ADMIN_SUPERVISOR: {
                    "summary": "Only supervisor or admin can use this router",
                    "value": {"detail": ErrorCode.USER_NOT_ADMIN_SUPERVISOR},
                }
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
                    },
                    ErrorCode.PERMANENTLY_BLOCKED: {
                        "summary": "Permanently blocked",
                        "value": {"detail": ErrorCode.PERMANENTLY_BLOCKED},
                    },
                    ErrorCode.UNBLOCKED_AFTER: {
                        "summary": "Raise blocking level",
                        "value": {"detail": "You are blocked now, please return after n days"},
                    },
                    ErrorCode.TEMPORARY_BLOCKED: {
                        "summary": "Temporary blocked",
                        "value": {"detail": ErrorCode.TEMPORARY_BLOCKED},
                    },
                    ErrorCode.WARNING_USER: {
                        "summary": "Warning user",
                        "value": {"detail": ErrorCode.WARNING_USER},
                    },
                }
            },
        },
    },
    status.HTTP_405_METHOD_NOT_ALLOWED: {
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
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.USER_INACTIVE: {
                        "summary": "Incorrect token or inactive user.",
                        "value": {"detail": "Unauthorized"
                                  },
                    }
                }
            },
        },
    },
    status.HTTP_403_FORBIDDEN: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.USER_NOT_AUTHENTICATED: {
                        "summary": "Missing token",
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
                }
                }
            },
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal sever error.",
    }
}

GET_RATING_SUPERVISOR_RESPONSE.update(SERVER_ERROR_AUTHORIZED_RESPONSE)
POST_RATING_RESPONSES.update(SERVER_ERROR_AUTHORIZED_RESPONSE)
GET_RATING_RESPONSE.update(SERVER_ERROR_AUTHORIZED_RESPONSE)
