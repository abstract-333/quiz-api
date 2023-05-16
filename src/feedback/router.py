import itertools
from collections import Counter
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from auth.base_config import current_user
from auth.models import User
from database import get_async_session
from feedback.models import feedback
from feedback.schemas import FeedbackRead, FeedbackCreate
from question.models import question
from utils.custom_exceptions import FeedbackAlreadySent, QuestionNotExists, RatingException, DuplicatedTitle
from utils.error_code import ErrorCode
from utils.result_into_list import ResultIntoList

feedback_router = APIRouter(
    prefix="/feedback",
    tags=["feedback"],
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

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        if not result:
            raise QuestionNotExists

        feedback_query = select(feedback).where(
            feedback.c.user_id == verified_user.id and feedback.c.question_id == added_feedback.question_id).order_by(
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
                                         question_id=added_feedback.question_id
                                         )

        stmt = insert(feedback).values(**feedback_create.dict())
        await session.execute(stmt)
        await session.commit()

        return {"status": "success",
                "data": feedback_create,
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


@feedback_router.get("/get/sent", name="feedback:get mine feedback", dependencies=[Depends(HTTPBearer())])
async def get_sent_feedback(page: int = 1, verified_user: User = Depends(current_user),
                            session: AsyncSession = Depends(get_async_session)):
    try:
        question_query = select(question).where(question.c.id == verified_user.id).limit(page - 1)
        result_proxy = await session.execute(question_query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        return {"status": "success",
                "data": result,
                "detail": None
                }

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
