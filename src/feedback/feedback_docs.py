from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from starlette import status

from rating.rating_docs import SERVER_ERROR_RESPONSE
from utils.error_code import ErrorCode

ADD_FEEDBACK_RESPONSES: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.FEEDBACK_ALREADY_SENT: {
                    "summary": "Feedback already sent",
                    "value": {"detail": "You already send a feedback for this question, please wait 12 hours"},
                }, ErrorCode.RATING_EXCEPTION: {
                    "summary": "Not valid rating",
                    "value": {"detail": ErrorCode.RATING_EXCEPTION},
                },
                }
            },
        },
    },
    status.HTTP_403_FORBIDDEN: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.NOT_ALLOWED_FEEDBACK_YOURSELF: {
                    "summary": "Not allowed feedback own questions",
                    "value": {"detail": ErrorCode.NOT_ALLOWED_FEEDBACK_YOURSELF},
                }, ErrorCode.USER_NOT_AUTHENTICATED: {
                    "summary": "Not authenticated",
                    "value": {"detail": "Not authenticated"},
                }
                }
            },
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.QUESTION_NOT_EXISTS: {
                    "summary": "Question not exists",
                    "value": {"detail": ErrorCode.QUESTION_NOT_EXISTS},
                }
                }
            },
        },
    },
}
GET_FEEDBACK_RECEIVED_RESPONSES: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.INVALID_PAGE: {
                        "summary": "Invalid page",
                        "value": {"detail": ErrorCode.INVALID_PAGE},
                    }
                }
            },
        },
    },
    status.HTTP_403_FORBIDDEN: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.USER_NOT_ADMIN_SUPERVISOR: {
                    "summary": "Only supervisor or admin can receive feedback",
                    "value": {"detail": ErrorCode.USER_NOT_ADMIN_SUPERVISOR},
                }, ErrorCode.USER_NOT_AUTHENTICATED: {
                    "summary": "Not authenticated",
                    "value": {"detail": "Not authenticated"},
                }}
            },
        },
    },
}
GET_FEEDBACK_SENT_RESPONSES: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.INVALID_PAGE: {
                        "summary": "Invalid page",
                        "value": {"detail": ErrorCode.INVALID_PAGE},
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
PATCH_FEEDBACK_RESPONSES: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.RATING_EXCEPTION: {
                    "summary": "Not valid rating",
                    "value": {"detail": ErrorCode.RATING_EXCEPTION},
                },
                }
            },
        },
    },
    status.HTTP_403_FORBIDDEN: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.NOT_ALLOWED_PATCH_FEEDBACK: {
                        "summary": "Patch feedback not allowed",
                        "value": {"detail": ErrorCode.NOT_ALLOWED_PATCH_FEEDBACK},
                    }
                    , ErrorCode.USER_NOT_AUTHENTICATED: {
                        "summary": "Not authenticated",
                        "value": {"detail": "Not authenticated"},
                    }
                }
            },
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.FEEDBACK_NOT_EXISTS: {
                    "summary": "Feedback not exists",
                    "value": {"detail": ErrorCode.FEEDBACK_NOT_EXISTS},
                }}
            },
        },
    },
    status.HTTP_405_METHOD_NOT_ALLOWED: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.FEEDBACK_NOT_EDITABLE: {
                    "summary": "You can't edit feedback now",
                    "value": {"detail": "You can edit the feedback for 15 minutes after you sent it"},
                }
                }
            }
        }
    },
}

DELETE_FEEDBACK_RESPONSES: OpenAPIResponseType = {

    status.HTTP_403_FORBIDDEN: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.NOT_ALLOWED_DELETE_FEEDBACK: {
                    "summary": "Only feedback writer can delete it",
                    "value": {"detail": ErrorCode.NOT_ALLOWED_DELETE_FEEDBACK},
                }, ErrorCode.USER_NOT_AUTHENTICATED: {
                    "summary": "Not authenticated",
                    "value": {"detail": "Not authenticated"},
                }
                }
            },
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.FEEDBACK_NOT_EXISTS: {
                    "summary": "Feedback not exists",
                    "value": {"detail": ErrorCode.FEEDBACK_NOT_EXISTS},
                }
                }
            }
        }
    },
    status.HTTP_405_METHOD_NOT_ALLOWED: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.NOT_ALLOWED_DELETE_FEEDBACK: {
                    "summary": "Can't delete feedback now",
                    "value": {"detail": "You can't delete feedback now, please wait 12 hours"},
                }
                }
            }
        }
    },
}


ADD_FEEDBACK_RESPONSES.update(SERVER_ERROR_RESPONSE)
GET_FEEDBACK_RECEIVED_RESPONSES.update(SERVER_ERROR_RESPONSE)
GET_FEEDBACK_SENT_RESPONSES.update(SERVER_ERROR_RESPONSE)
PATCH_FEEDBACK_RESPONSES.update(SERVER_ERROR_RESPONSE)
DELETE_FEEDBACK_RESPONSES.update(SERVER_ERROR_RESPONSE)
