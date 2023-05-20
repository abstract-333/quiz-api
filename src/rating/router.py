import itertools

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from auth.base_config import current_user
from auth.models import user, User
from database import get_async_session
from feedback.models import feedback
from rating.rating_db import get_rating_user_id, update_rating_db, insert_rating_db
from rating.schemas import RatingRead, RatingUpdate, RatingCreate
from utils.custom_exceptions import QuestionsInvalidNumber
from utils.result_into_list import ResultIntoList

rating_router = APIRouter(
    prefix="/rating",
    tags=["Rating"],
)


@rating_router.get("/supervisor", name="supervisor:get best rating", dependencies=[Depends(HTTPBearer())])
async def add_feedback(session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(
            user.c.username,
            (func.sum(feedback.c.rating) / func.count(feedback.c.id)).label('average_rating'),
            func.count(feedback.c.id).label('count_of_rates'))\
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


@rating_router.post("/student", name="student:add rating", dependencies=[Depends(HTTPBearer())])
async def add_rating(rating_read: RatingRead, verified_user: User = Depends(current_user),
                     session: AsyncSession = Depends(get_async_session)):
    try:
        if rating_read.questions_number not in range(10, 51) or rating_read.solved not in range(51):
            raise QuestionsInvalidNumber

        if rating_read.solved > rating_read.questions_number:
            raise QuestionsInvalidNumber

        rating_user_row = await get_rating_user_id(user_id=verified_user.id, session=session)

        if rating_user_row:

            total_number_questions = rating_read.questions_number + rating_user_row[0]["questions_number"]
            old_number_solved = rating_user_row[0]["percent_solved"] * rating_user_row[0]["questions_number"]
            total_number_solved = rating_read.solved + old_number_solved
            percent_solved = total_number_solved / total_number_questions

            updated_rating = RatingUpdate(questions_number=total_number_questions,
                                          percent_solved=percent_solved,
                                          user_id=rating_read.user_id)

            await update_rating_db(rating_id=rating_user_row[0]["id"], session=session, updated_rating=updated_rating)

            return {"status": "success",
                    "data": updated_rating,
                    "detail": None
                    }

        else:
            percent_solved = rating_read.solved / rating_read.questions_number

            rating_create = RatingCreate(user_id=rating_read.user_id,
                                         university_id=verified_user.university_id,
                                         questions_number=rating_read.questions_number,
                                         percent_solved=percent_solved)

            await insert_rating_db(rating_create=rating_create, session=session)

            return {"status": "success",
                    "data": rating_read,
                    "detail": None
                    }

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


