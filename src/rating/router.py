import itertools

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import select, func, desc, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth.base_config import current_user
from auth.models import user, User
from database import get_async_session
from feedback.models import feedback
from rating.models import rating
from rating.rating_db import rating_user_id
from rating.schemas import RatingRead, RatingUpdate, RatingCreate
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
            func.count(feedback.c.id).label('count_of_rates')
        ).join(feedback, user.c.id == feedback.c.question_author_id). \
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
        rating_user = await rating_user_id(user_id=verified_user.id, session=session)

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
        rating_user_row = await rating_user_id(user_id=verified_user.id, session=session)

        if rating_user_row:
            total_number_questions = rating_read.questions_number + rating_user_row[0]["questions_number"]
            old_number_solved = rating_user_row[0]["percent_solved"] * rating_user_row[0]["questions_number"]
            total_number_solved = rating_read.solved + old_number_solved
            percent_solved = total_number_solved / total_number_questions

            updated_rating = RatingUpdate(questions_number=total_number_questions,
                                          percent_solved=percent_solved)

            stmt = update(rating).values(**updated_rating.dict()).where(rating.c.id == rating_user_row[0]["id"])
            await session.execute(stmt)
            await session.commit()

        else:
            percent_solved = rating_read.solved / rating_read.questions_number

            rating_create = RatingCreate(user_id=verified_user.id,
                                         university_id=verified_user.university_id,
                                         questions_number=rating_read.questions_number,
                                         percent_solved=percent_solved)

            stmt = insert(rating).values(**rating_create.dict())
            await session.execute(stmt)
            await session.commit()

        return {"Success"}

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
