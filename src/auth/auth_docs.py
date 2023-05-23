from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from starlette import status

from utils.error_code import ErrorCode

REQUEST_VERIFY_EMAIL_RESPONSE: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.USER_INACTIVE: {
                    "summary": "User is inactive.",
                    "value": {"detail": ErrorCode.USER_INACTIVE},
                }, ErrorCode.USER_NOT_EXISTS: {
                    "summary": "User not exists with this email.",
                    "value": {"detail": ErrorCode.USER_NOT_EXISTS},
                },
                    ErrorCode.VERIFY_USER_ALREADY_VERIFIED: {
                        "summary": "The user is already verified.",
                        "value": {
                            "detail": ErrorCode.VERIFY_USER_ALREADY_VERIFIED
                        },
                    },
                }
            }
        },
    }
}
VERIFY_EMAIL_RESPONSE: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.VERIFY_USER_BAD_TOKEN: {
                    "summary": "Invalid verify token or user with this email does not exists",
                    "value": {"detail": ErrorCode.VERIFY_USER_BAD_TOKEN},
                }
                    ,
                    ErrorCode.VERIFY_USER_ALREADY_VERIFIED: {
                        "summary": "The user is already verified.",
                        "value": {
                            "detail": ErrorCode.VERIFY_USER_ALREADY_VERIFIED
                        },
                    },
                }
            }
        },
    }
}


FORGET_PASSWORD_RESPONSES: OpenAPIResponseType = {
    status.HTTP_404_NOT_FOUND: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {"USER_INACTIVE_OR_NOT_EXISTS": {
                    "summary": "User inactive or not exists",
                    "value": {"detail": "USER_INACTIVE_OR_NOT_EXISTS"},
                },
                }
            }
        },
    },
}

RESET_PASSWORD_RESPONSES: OpenAPIResponseType = {status.HTTP_401_UNAUTHORIZED: {
    "model": ErrorModel,
    "content": {
        "application/json": {
            "examples": {ErrorCode.USER_INACTIVE: {
                "summary": "Bad or expired token.",
                "value": {"detail": ErrorCode.USER_INACTIVE},
            }, ErrorCode.USER_NOT_EXISTS: {
                "summary": "Bad or expired token.",
                "value": {"detail": ErrorCode.USER_NOT_EXISTS},
            },
                ErrorCode.RESET_PASSWORD_BAD_TOKEN: {
                    "summary": "Bad or expired token.",
                    "value": {"detail": ErrorCode.RESET_PASSWORD_BAD_TOKEN},
                },
                ErrorCode.RESET_PASSWORD_INVALID_PASSWORD: {
                    "summary": "Password validation failed."
                    ,
                    "value": {
                        "detail": ("Password should be at least 8 characters",
                                   "Password should not contain email",
                                   "Password must contain at least one uppercase letter",
                                   "Password must contain at least one lowercase letter",
                                   "Password must contain at least one digit",
                                   "Password must contain at least one special character",
                                   ),
                    },
                },
            }
        }
    },
}
}

