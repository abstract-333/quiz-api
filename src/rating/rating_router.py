import itertools
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from auth.base_config import current_user
from auth.auth_models import user, User
from blacklist.blacklist_service import get_blocking_level, manage_blocking_level, get_blocking_time
from database import get_async_session
from feedback.feedback_db import get_rating_supervisor_db
from feedback.feedback_models import feedback
from rating.rating_docs import SERVER_ERROR_AUTHORIZED_RESPONSE, POST_RATING_RESPONSES, GET_RATING_RESPONSE, \
    GET_RATING_SUPERVISOR_RESPONSE
from rating.rating_models import rating
from rating.rating_db import get_rating_user_id, update_rating_db, insert_rating_db, get_last_rating_user
from rating.rating_schemas import RatingUpdate, RatingCreate, RatingRead
from university.university_models import university
from utilties.custom_exceptions import QuestionsInvalidNumber, NotUser, OutOfUniversityIdException, \
    UserNotAdminSupervisor, AddedToBlacklist, RaisingBlockingLevel, HighestBlockingLevel, WarnsUserException, \
    BlockedReturnAfter
from utilties.error_code import ErrorCode
from utilties.result_into_list import ResultIntoList
from university.university_db import check_university_valid
from warning.warning_service import manage_warning_level

rating_router = APIRouter(
    prefix="/rating",
    tags=["Rating"],
)


@rating_router.get("/supervisor", name="supervisor:get best rating", dependencies=[Depends(HTTPBearer())],
                   responses=SERVER_ERROR_AUTHORIZED_RESPONSE)
async def add_feedback(verified_user: User = Depends(current_user)
                       , session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(
            user.c.username,
            (func.sum(feedback.c.rating) / func.count(feedback.c.id)).label('average_rating'),
            func.count(feedback.c.id).label('count_of_rates')) \
            .join(feedback, user.c.id == feedback.c.question_author_id) \
            .group_by(feedback.c.question_author_id). \
            having((func.sum(feedback.c.rating) / func.count(feedback.c.id)) > 2.5) \
            .order_by(desc((func.sum(feedback.c.rating) / func.count(feedback.c.id)))) \
            .limit(10)

        result_proxy = await session.execute(query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        return result

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@rating_router.get("/student", name="student:get best rating", dependencies=[Depends(HTTPBearer())],
                   responses=SERVER_ERROR_AUTHORIZED_RESPONSE)
async def get_rating_students(verified_user: User = Depends(current_user)
                              , session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(
            user.c.id,
            user.c.username,
            func.sum(rating.c.questions_number).label('questions_number'),
            func.sum(rating.c.solved).label('solved')) \
            .join_from(rating, user, rating.c.user_id == user.c.id) \
            .group_by(rating.c.user_id) \
            .order_by(desc(func.sum(rating.c.solved))).limit(10)

        result_proxy = await session.execute(query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        return result
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@rating_router.get("/university-students", name="student:get best rating by university",
                   dependencies=[Depends(HTTPBearer())], responses=GET_RATING_RESPONSE)
async def get_rating_students_university(university_id: int, verified_user: User = Depends(current_user)
                                         , session: AsyncSession = Depends(get_async_session)):
    try:
        await check_university_valid(university_id=university_id, session=session)

        query = select(
            user.c.id,
            user.c.username,
            func.sum(rating.c.questions_number).label('questions_number'),
            func.sum(rating.c.solved).label('solved')).where(rating.c.university_id == university_id) \
            .join_from(rating, user, rating.c.user_id == user.c.id) \
            .group_by(rating.c.user_id) \
            .order_by(desc(func.sum(rating.c.solved))).limit(10)

        result_proxy = await session.execute(query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        return result

    except OutOfUniversityIdException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.OUT_OF_UNIVERSITY_ID)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@rating_router.get("/university", name="university:get best rating",
                   dependencies=[Depends(HTTPBearer())],
                   responses=SERVER_ERROR_AUTHORIZED_RESPONSE)
async def get_rating_universities(verified_user: User = Depends(current_user)
                                  , session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(
            rating.c.university_id,
            university.c.name,
            func.sum(rating.c.questions_number).label('question_number'),
            func.sum(rating.c.solved).label('solved')) \
            .join_from(university, rating, rating.c.university_id == university.c.id) \
            .group_by(rating.c.university_id) \
            .order_by(desc(func.sum(rating.c.solved))).limit(10)

        result_proxy = await session.execute(query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        return result
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@rating_router.get(
    path="/student/me",
    name="student:get rating",
    dependencies=[Depends(HTTPBearer())],
    responses=SERVER_ERROR_AUTHORIZED_RESPONSE
)
async def get_rating_me(
        verified_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        rating_user = await get_rating_user_id(user_id=verified_user.id, session=session)

        return {"status": "success",
                "data": rating_user,
                "detail": None
                }

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@rating_router.get(
    path="/supervisor/me",
    name="supervisor:get rating",
    dependencies=[Depends(HTTPBearer())],
    responses=GET_RATING_SUPERVISOR_RESPONSE
)
async def get_rating_me(
        verified_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    """Get supervisor rating"""
    try:
        if verified_user.role_id == 1:  # user can't add questions
            raise UserNotAdminSupervisor

        result = await get_rating_supervisor_db(user_id=verified_user.id, session=session)

        return {"status": "success",
                "data": result,
                "detail": None
                }

    except UserNotAdminSupervisor:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail=ErrorCode.USER_NOT_ADMIN_SUPERVISOR)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@rating_router.post(
    path="/student",
    name="student:add rating",
    dependencies=[Depends(HTTPBearer())],
    responses=POST_RATING_RESPONSES
)
async def add_rating(
        rating_read: RatingRead,
        verified_user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    global unblocked_after
    try:
        unblocked_after = await get_blocking_time(user_id=verified_user.id, session=session)

        if unblocked_after is not None:
            raise BlockedReturnAfter

        if verified_user.role_id != 1:
            raise NotUser

        if rating_read.solved > rating_read.questions_number:
            raise QuestionsInvalidNumber

        if rating_read.questions_number not in range(30, 51) or rating_read.solved not in range(51):
            raise QuestionsInvalidNumber

        solved = rating_read.solved
        questions_number = rating_read.questions_number

        if solved // questions_number < 0.11 or solved < 3:
            # Get blocking level if exits and update it
            blocking_level = await get_blocking_level(user_id=verified_user.id, session=session)

            if blocking_level is not None:
                await manage_blocking_level(user_id=verified_user.id, session=session)

            else:
                # Manage user's warnings
                await manage_warning_level(user_id=verified_user.id, session=session)

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

    except WarnsUserException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.WARNING_USER)

    except (RaisingBlockingLevel, AddedToBlacklist):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.TEMPORARY_BLOCKED
        )
    except BlockedReturnAfter:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You are blocked now, please return after {unblocked_after} days"
        )

    except HighestBlockingLevel:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.PERMANENTLY_BLOCKED)

    except QuestionsInvalidNumber:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.QUESTIONS_NUMBER_INVALID)

    except NotUser:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail=ErrorCode.ONLY_USER)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
