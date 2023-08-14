from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from starlette import status

from api.rating.rating_docs import SERVER_ERROR_AUTHORIZED_RESPONSE
from utilties.error_code import ErrorCode

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
    status.HTTP_404_NOT_FOUND: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.QUESTION_NOT_FOUND: {
                    "summary": "Question not exists",
                    "value": {"detail": ErrorCode.QUESTION_NOT_FOUND},
                }
                }
            },
        },
    },
    status.HTTP_405_METHOD_NOT_ALLOWED: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.NOT_ALLOWED_FEEDBACK_YOURSELF: {
                    "summary": "Not allowed feedback own questions",
                    "value": {"detail": ErrorCode.NOT_ALLOWED_FEEDBACK_YOURSELF},
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
    status.HTTP_405_METHOD_NOT_ALLOWED: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.USER_NOT_ADMIN_SUPERVISOR: {
                    "summary": "Only supervisor or admin_panel can receive feedback",
                    "value": {"detail": ErrorCode.USER_NOT_ADMIN_SUPERVISOR},
                }
                }
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
    status.HTTP_404_NOT_FOUND: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.FEEDBACK_NOT_FOUND: {
                    "summary": "Feedback not exists",
                    "value": {"detail": ErrorCode.FEEDBACK_NOT_FOUND},
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
                    "value": {"detail": "You can edit the feedback during 15 minutes after you it"},
                },
                    ErrorCode.NOT_ALLOWED_PATCH_FEEDBACK: {
                        "summary": "Patch feedback not allowed",
                        "value": {"detail": ErrorCode.NOT_ALLOWED_PATCH_FEEDBACK},
                    }
                }
            }
        }
    },
}

DELETE_FEEDBACK_RESPONSES: OpenAPIResponseType = {
    status.HTTP_404_NOT_FOUND: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.FEEDBACK_NOT_FOUND: {
                    "summary": "Feedback not exists",
                    "value": {"detail": ErrorCode.FEEDBACK_NOT_FOUND},
                }
                }
            }
        }
    },
    status.HTTP_405_METHOD_NOT_ALLOWED: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.NOT_ALLOWED_DELETE_FEEDBACK: {
                        "summary": "Can't delete feedback now",
                        "value": {"detail": "You can't delete feedback now, please wait 12 hours"},
                    },
                    ErrorCode.ONLY_FEEDBACK_AUTHOR_DELETE: {
                        "summary": "Only feedback author can delete it",
                        "value": {"detail": ErrorCode.ONLY_FEEDBACK_AUTHOR_DELETE},
                    }
                }
            }
        }
    },
}

ADD_FEEDBACK_RESPONSES.update(SERVER_ERROR_AUTHORIZED_RESPONSE)
GET_FEEDBACK_RECEIVED_RESPONSES.update(SERVER_ERROR_AUTHORIZED_RESPONSE)
GET_FEEDBACK_SENT_RESPONSES.update(SERVER_ERROR_AUTHORIZED_RESPONSE)
PATCH_FEEDBACK_RESPONSES.update(SERVER_ERROR_AUTHORIZED_RESPONSE)
DELETE_FEEDBACK_RESPONSES.update(SERVER_ERROR_AUTHORIZED_RESPONSE)
