import itertools
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from sqlalchemy import insert, select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from auth.base_config import current_user
from auth.models import User
from database import get_async_session
from feedback.models import feedback
from feedback.schemas import FeedbackRead, FeedbackUpdate, FeedbackCreate
from question.models import question
from utils.custom_exceptions import FeedbackAlreadySent, QuestionNotExists, RatingException, DuplicatedTitle, \
    InvalidPage, FeedbackNotExists, FeedbackNotEditable, UserNotAdminSupervisor
from utils.error_code import ErrorCode
from utils.result_into_list import ResultIntoList

feedback_router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
)

ADD_FEEDBACK_QUESTION_RESPONSES: OpenAPIResponseType = {
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
                "examples": {ErrorCode.USER_NOT_AUTHENTICATED: {
                    "summary": "Not authenticated",
                    "value": {"detail": "Not authenticated"},
                }}
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
                }}
            },
        },
    },
    status.HTTP_409_CONFLICT: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.FEEDBACK_ALREADY_SENT: {
                    "summary": "Feedback already sent",
                    "value": {"detail": "You already send a feedback for this question, please wait 12 hours"},
                }
                }
            }
        }
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal sever error.",
    }
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
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal sever error.",
    }
}
PATCH_FEEDBACK_QUESTION_RESPONSES: OpenAPIResponseType = {
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
                "examples": {ErrorCode.USER_NOT_AUTHENTICATED: {
                    "summary": "Not authenticated",
                    "value": {"detail": "Not authenticated"},
                }}
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
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal sever error.",
    }
}


@feedback_router.post("/add", name="feedback:add feedback", dependencies=[Depends(HTTPBearer())],
                      responses=ADD_FEEDBACK_QUESTION_RESPONSES)
async def add_feedback(added_feedback: FeedbackRead, verified_user: User = Depends(current_user),
                       session: AsyncSession = Depends(get_async_session)):
    try:
        if added_feedback.rating not in (0, 1, 2, 3, 4, 5):
            raise RatingException

        question_query = select(question).where(
            question.c.id == added_feedback.question_id)
        result_proxy = await session.execute(question_query)

        result_question = ResultIntoList(result_proxy=result_proxy)
        result_question = list(itertools.chain(result_question.parse()))

        if not result_question:
            raise QuestionNotExists

        feedback_query = select(feedback).where(
            feedback.c.question_id == added_feedback.question_id and feedback.c.user_id == verified_user.id).order_by(
            feedback.c.added_at)
        result_proxy = await session.execute(feedback_query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        remaining_time = None

        if result:
            remaining_time = (datetime.utcnow() - result[0]["added_at"]).seconds
            remaining_time = 3600 * 12 - remaining_time
            remaining_time = remaining_time // 3600

            if remaining_time > 0:
                raise FeedbackAlreadySent

            for row in result:
                if row["feedback_title"] == added_feedback.feedback_title:
                    raise DuplicatedTitle

        feedback_create = FeedbackCreate(rating=added_feedback.rating,
                                         feedback_title=added_feedback.feedback_title,
                                         user_id=verified_user.id,
                                         question_id=added_feedback.question_id,
                                         question_author_id=result_question[0]["added_by"]
                                         )

        stmt = insert(feedback).values(**feedback_create.dict())
        await session.execute(stmt)
        await session.commit()

        return {"status": "success",
                "data": added_feedback,
                "detail": None
                }

    except RatingException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.RATING_EXCEPTION)

    except QuestionNotExists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorCode.QUESTION_NOT_EXISTS)

    except DuplicatedTitle:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ErrorCode.DUPLICATED_TITLE)

    except FeedbackAlreadySent:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"You already send a feedback for this question, please wait {remaining_time} hours")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@feedback_router.get("/get/sent", name="feedback:get sent feedback", dependencies=[Depends(HTTPBearer())],
                     responses=GET_FEEDBACK_SENT_RESPONSES)
async def get_sent_feedback(page: int = 1, verified_user: User = Depends(current_user),
                            session: AsyncSession = Depends(get_async_session)):
    try:
        if page < 1:
            raise InvalidPage

        question_query = select(feedback).where(feedback.c.user_id == verified_user.id).order_by(desc(feedback.c.added_at)).offset(page - 1).offset(
            page - 1).limit(10)
        result_proxy = await session.execute(question_query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        return {"status": "success",
                "data": result,
                "detail": None
                }

    except InvalidPage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.INVALID_PAGE)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@feedback_router.get("/get/received", name="feedback:get received feedback", dependencies=[Depends(HTTPBearer())],
                     responses=GET_FEEDBACK_SENT_RESPONSES)
async def get_sent_feedback(page: int = 1, verified_user: User = Depends(current_user),
                            session: AsyncSession = Depends(get_async_session)):
    try:
        if verified_user.role_id == 1:
            raise UserNotAdminSupervisor

        if page < 1:
            raise InvalidPage

        question_query = select(feedback).where(feedback.c.question_author_id == verified_user.id).order_by(desc(feedback.c.added_at)).offset(page-1).limit(10)
        result_proxy = await session.execute(question_query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        return {"status": "success",
                "data": result,
                "detail": None
                }

    except UserNotAdminSupervisor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorCode.USER_NOT_ADMIN_SUPERVISOR)

    except InvalidPage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.INVALID_PAGE)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@feedback_router.patch("/patch", name="feedback:patch feedback", dependencies=[Depends(HTTPBearer())],
                       responses=PATCH_FEEDBACK_QUESTION_RESPONSES)
async def add_feedback(feedback_id: int, edited_feedback: FeedbackUpdate, verified_user: User = Depends(current_user),
                       session: AsyncSession = Depends(get_async_session)):
    try:
        if edited_feedback.rating not in (0, 1, 2, 3, 4, 5):
            raise RatingException

        feedback_query = select(feedback).where(
            feedback.c.id == feedback_id).order_by(feedback.c.added_at)
        result_proxy = await session.execute(feedback_query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        if not result:
            raise FeedbackNotExists

        if result:
            remaining_time = (datetime.utcnow() - result[0]["added_at"]).seconds
            remaining_time = 900 - remaining_time
            remaining_time = remaining_time // 60

            if abs(remaining_time) > 15:
                raise FeedbackNotEditable

            for row in result:
                if row["feedback_title"] == edited_feedback.feedback_title and row["rating"] == edited_feedback.rating:
                    returned_object = FeedbackCreate(rating=row["rating"],
                                                     feedback_title=row["feedback_title"],
                                                     user_id=row["user_id"],
                                                     question_id=row["question_id"],
                                                     question_author_id=row["question_author_id"]
                                                     )
                    return {"status": "success",
                            "data": returned_object,
                            "detail": None
                            }

        feedback_create = FeedbackCreate(rating=edited_feedback.rating,
                                         feedback_title=edited_feedback.feedback_title,
                                         user_id=result[0]["user_id"],
                                         question_id=result[0]["question_id"]
                                         )

        stmt = update(feedback).values(**feedback_create.dict()).where(feedback.c.id == feedback_id)
        await session.execute(stmt)
        await session.commit()

        return {"status": "success",
                "data": feedback_create,
                "detail": None
                }

    except RatingException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.RATING_EXCEPTION)

    except FeedbackNotExists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorCode.FEEDBACK_NOT_EXISTS)

    except FeedbackNotEditable:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail="You can edit the feedback for 15 minutes after you sent it")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
