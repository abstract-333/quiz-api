from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from starlette import status

from rating.rating_docs import SERVER_ERROR_UNAUTHORIZED_RESPONSE, SERVER_ERROR_AUTHORIZED_RESPONSE
from utilties.error_code import ErrorCode

PATCH_ME_RESPONSE: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS: {
                    "summary": "A user with this email already exists.",
                    "value": {"detail": ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS},
                },
                    ErrorCode.OUT_OF_UNIVERSITY_ID: {
                        "summary": "Wrong entered university_id",
                        "value": {"detail": ErrorCode.OUT_OF_UNIVERSITY_ID},
                    },
                    ErrorCode.OUT_OF_SECTION_ID: {
                        "summary": "Wrong entered section_id",
                        "value": {"detail": ErrorCode.OUT_OF_SECTION_ID},
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
    },
    status.HTTP_405_METHOD_NOT_ALLOWED: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.NOT_ALLOWED_PATCHING: {
                    "summary": "Editing yourself not allowed",
                    "value": {"detail": ErrorCode.NOT_ALLOWED_PATCHING},
                },
                }
            }
        },
    },
}

PATCH_USER_ID_RESPONSE: OpenAPIResponseType = {
    status.HTTP_403_FORBIDDEN: {"description": "Not a superuser.",
                                },
}

GET_DELETE_USER_ID_RESPONSE: OpenAPIResponseType = {
    status.HTTP_403_FORBIDDEN: {
        "description": "Not a superuser.",
    },
    status.HTTP_404_NOT_FOUND: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.USER_NOT_EXISTS: {
                    "summary": "The user does not exist.",
                    "value": {"detail": ErrorCode.USER_NOT_EXISTS},
                },
                },
            }
        },
    },
}
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
                "examples": {ErrorCode.USER_INACTIVE_OR_NOT_EXISTS: {
                    "summary": "User inactive or not exists",
                    "value": {"detail": ErrorCode.USER_INACTIVE_OR_NOT_EXISTS},
                },
                }
            }
        },
    },
}

RESET_PASSWORD_RESPONSES: OpenAPIResponseType = {
    status.HTTP_401_UNAUTHORIZED: {
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
                }
            }
        },
    },
    status.HTTP_400_BAD_REQUEST: {
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
    },

}
GET_DELETE_USER_ID_RESPONSE.update(SERVER_ERROR_AUTHORIZED_RESPONSE)

PATCH_ME_RESPONSE.update(SERVER_ERROR_AUTHORIZED_RESPONSE)

PATCH_USER_ID_RESPONSE.update(PATCH_ME_RESPONSE)
PATCH_USER_ID_RESPONSE.pop(status.HTTP_405_METHOD_NOT_ALLOWED, None)

REQUEST_VERIFY_EMAIL_RESPONSE.update(SERVER_ERROR_UNAUTHORIZED_RESPONSE)
VERIFY_EMAIL_RESPONSE.update(SERVER_ERROR_UNAUTHORIZED_RESPONSE)
FORGET_PASSWORD_RESPONSES.update(SERVER_ERROR_UNAUTHORIZED_RESPONSE)
RESET_PASSWORD_RESPONSES.update(SERVER_ERROR_UNAUTHORIZED_RESPONSE)
