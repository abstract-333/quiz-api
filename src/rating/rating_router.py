import itertools
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from auth.base_config import current_user
from auth.auth_models import user, User
from database import get_async_session
from feedback.feedback_models import feedback
from rating.rating_docs import POST_RATING_RESPONSES
from rating.rating_models import rating
from rating.rating_db import get_rating_user_id, update_rating_db, insert_rating_db, get_last_rating_user
from rating.rating_schemas import RatingRead, RatingUpdate, RatingCreate
from utils.custom_exceptions import QuestionsInvalidNumber, UserNotAdminSupervisor
from utils.error_code import ErrorCode
from utils.result_into_list import ResultIntoList

rating_router = APIRouter(
    prefix="/rating",
    tags=["Rating"],
)


@rating_router.get("/supervisor", name="supervisor:get best rating", dependencies=[Depends(HTTPBearer())])
async def add_feedback(verified_user: User = Depends(current_user)
                       , session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(
            user.c.username,
            (func.sum(feedback.c.rating) / func.count(feedback.c.id)).label('average_rating'),
            func.count(feedback.c.id).label('count_of_rates')) \
            .join(feedback, user.c.id == feedback.c.question_author_id). \
            order_by(desc((func.sum(feedback.c.rating) / func.count(feedback.c.id)))) \
            .group_by(feedback.c.question_author_id). \
            having((func.sum(feedback.c.rating) / func.count(feedback.c.id)) > 2.5). \
            limit(10)

        result_proxy = await session.execute(query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        return result
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@rating_router.get("/student", name="student:get best rating", dependencies=[Depends(HTTPBearer())])
async def get_rating_students(verified_user: User = Depends(current_user)
                              , session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(
            user.c.username,
            rating.c.questions_number, rating.c.solved) \
            .join_from(rating, user, rating.c.user_id == user.c.id). \
            order_by(desc(rating.c.solved)) \
            .limit(10)

        result_proxy = await session.execute(query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        return result
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@rating_router.get("/student/me", name="student:get rating", dependencies=[Depends(HTTPBearer())])
async def get_rating_me(verified_user: User = Depends(current_user),
                        session: AsyncSession = Depends(get_async_session)):
    try:
        rating_user = await get_rating_user_id(user_id=verified_user.id, session=session)

        return {"status": "success",
                "data": rating_user,
                "detail": None
                }

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@rating_router.post("/student", name="student:add rating", dependencies=[Depends(HTTPBearer())],
                    responses=POST_RATING_RESPONSES)
async def add_rating(rating_read: RatingRead, verified_user: User = Depends(current_user),
                     session: AsyncSession = Depends(get_async_session)):
    try:
        if verified_user.role_id != 1:
            raise UserNotAdminSupervisor

        if rating_read.solved > rating_read.questions_number:
            raise QuestionsInvalidNumber

        if rating_read.questions_number not in range(51) or rating_read.solved not in range(51):
            raise QuestionsInvalidNumber

        last_rating = await get_last_rating_user(user_id=verified_user.id, session=session)

        if last_rating and last_rating[0]["added_at"].date() == datetime.now().date():
            total_questions = rating_read.questions_number + last_rating[0]["questions_number"]
            total_solved = rating_read.solved + last_rating[0]["solved"]

            rating_update = RatingUpdate(questions_number=total_questions,
                                         solved=total_solved)
            await update_rating_db(rating_id=last_rating[0]["id"], updated_rating=rating_update, session=session)

            return {"status": "success",
                    "data": None,
                    "detail": None
                    }

        else:
            rating_create = RatingCreate(user_id=verified_user.id,
                                         university_id=verified_user.university_id,
                                         questions_number=rating_read.questions_number,
                                         solved=rating_read.solved)

            await insert_rating_db(rating_create=rating_create, session=session)

            return {"status": "success",
                    "data": None,
                    "detail": None
                    }
    except UserNotAdminSupervisor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorCode.USER_NOT_ADMIN_SUPERVISOR)

    except QuestionsInvalidNumber:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.QUESTIONS_NUMBER_INVALID)


    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
