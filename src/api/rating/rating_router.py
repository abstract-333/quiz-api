import itertools
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from sqlalchemy import select, func, desc
from starlette import status

from api.auth.auth_models import user
from api.blacklist.blacklist_service import get_blocking_level, manage_blocking_level, get_blocking_time
from api.feedback.feedback_db import get_rating_supervisor_db
from api.feedback.feedback_models import feedback
from api.rating.rating_db import get_rating_user_id, update_rating_db, insert_rating_db, get_last_rating_user
from api.rating.rating_docs import (
    SERVER_ERROR_AUTHORIZED_RESPONSE,
    POST_RATING_RESPONSES,
    GET_RATING_RESPONSE,
    GET_RATING_SUPERVISOR_RESPONSE
)
from api.rating.rating_errors import Errors as RatingErrors
from api.rating.rating_models import rating
from api.rating.rating_schemas import RatingUpdate, RatingCreate, RatingRead
from api.university.university_errors import Errors as UniversityErrors
from api.university.university_models import university
from api.university.unviversity_service import UniversityService
from api.warning.warning_service import manage_warning_level
from core.dependecies import UOWDep, CurrentUser, Session
from utilties.custom_exceptions import (
    QuestionsInvalidNumber,
    NotUser,
    OutOfUniversityIdException,
    UserNotAdminSupervisor,
    AddedToBlacklist,
    RaisingBlockingLevel,
    HighestBlockingLevel,
    WarnsUserException,
    BlockedReturnAfter
)
from utilties.result_into_list import ResultIntoList

rating_router = APIRouter(
    prefix="/rating",
    tags=["Rating"],
)


@rating_router.get("/supervisor", name="supervisor:get best rating", dependencies=[Depends(HTTPBearer())],
                   responses=SERVER_ERROR_AUTHORIZED_RESPONSE)
async def add_feedback(
        verified_user: CurrentUser,
        session: Session
):
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
async def get_rating_students(
        verified_user: CurrentUser,
        session: Session
):
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
async def get_rating_students_university(
        uow: UOWDep,
        verified_user: CurrentUser,
        session: Session,
        university_id: int = Query(gt=0),
):
    try:
        # Check whether entered university_id is valid
        await UniversityService().get_university_by_id(uow=uow, university_id=university_id)

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
        raise UniversityErrors.invalid_university_index_400

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@rating_router.get("/university", name="university:get best rating",
                   dependencies=[Depends(HTTPBearer())],
                   responses=SERVER_ERROR_AUTHORIZED_RESPONSE)
async def get_rating_universities(
        verified_user: CurrentUser,
        session: Session
):
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
        verified_user: CurrentUser,
        session: Session
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
        verified_user: CurrentUser,
        session: Session
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
        raise RatingErrors.user_not_allowed_405

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
        verified_user: CurrentUser,
        session: Session
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
        raise RatingErrors.warns_user_400

    except (RaisingBlockingLevel, AddedToBlacklist):
        raise RatingErrors.temporary_blocked_400

    except BlockedReturnAfter:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You are blocked now, please return after {unblocked_after} days"
        )

    except HighestBlockingLevel:
        raise RatingErrors.permanently_blocked_400

    except QuestionsInvalidNumber:
        raise RatingErrors.number_of_questions_invalid_400

    except NotUser:
        raise RatingErrors.only_user_can_access_405

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
