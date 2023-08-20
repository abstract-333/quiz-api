from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from sqlalchemy import insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.feedback.feedback_db import (
    feedback_sent_db,
    feedback_received_db,
    feedback_by_id_db,
    feedback_question_id_user_id_db,
    delete_feedback_id,
    get_remaining_time
)
from api.feedback.feedback_docs import (
    ADD_FEEDBACK_RESPONSES,
    GET_FEEDBACK_SENT_RESPONSES,
    PATCH_FEEDBACK_RESPONSES,
    GET_FEEDBACK_RECEIVED_RESPONSES,
    DELETE_FEEDBACK_RESPONSES
)
from api.feedback.feedback_errors import Errors
from api.feedback.feedback_models import feedback
from api.feedback.feedback_schemas import FeedbackRead, FeedbackUpdate, FeedbackCreate
from api.question.question_db import get_question_id_db
from core.dependecies import CurrentUser
from database import get_async_session
from utilties.custom_exceptions import (
    FeedbackAlreadySent,
    QuestionNotFound,
    RatingException,
    DuplicatedTitle,
    InvalidPage,
    FeedbackNotFound,
    FeedbackNotEditable,
    UserNotAdminSupervisor,
    NotAllowedDeleteBeforeTime,
    NotAllowed
)

feedback_router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
)


@feedback_router.post("/add", name="feedback:add feedback", dependencies=[Depends(HTTPBearer())],
                      responses=ADD_FEEDBACK_RESPONSES)
async def add_feedback(added_feedback: FeedbackRead, verified_user: CurrentUser,
                       session: AsyncSession = Depends(get_async_session)):
    try:

        if added_feedback.rating not in (1, 2, 3, 4, 5):
            raise RatingException

        result_question = await get_question_id_db(question_id=added_feedback.question_id, session=session)

        if not result_question:
            raise QuestionNotFound

        else:
            if result_question[0]["added_by"] == verified_user.id:
                raise NotAllowed

        result = await feedback_question_id_user_id_db(question_id=added_feedback.question_id,
                                                       user_id=verified_user.id, session=session)

        remaining_time = None

        if result:
            remaining_time = await get_remaining_time(result[0]["added_at"], target_time=3600 * 12)
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

        stmt = insert(feedback).values(**feedback_create.model_dump())
        await session.execute(stmt)
        await session.commit()

        return {"status": "success",
                "data": added_feedback,
                "detail": None
                }

    except RatingException:
        raise Errors.rating_mark_400

    except QuestionNotFound:
        raise Errors.question_not_exists_404

    except NotAllowed:
        raise Errors.not_allowed_405

    except DuplicatedTitle:
        raise Errors.feedback_duplicated_title_409

    except FeedbackAlreadySent:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"You already send a feedback for this question, please wait {remaining_time} hours")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@feedback_router.get("/get/sent", name="feedback:get sent feedback", dependencies=[Depends(HTTPBearer())],
                     responses=GET_FEEDBACK_SENT_RESPONSES)
async def get_sent_feedback(
        verified_user: CurrentUser,
        page: int = Query(gt=0, default=1),
        session: AsyncSession = Depends(get_async_session)):
    try:
        if page < 1:
            raise InvalidPage

        result = await feedback_sent_db(page=page, session=session, user_id=verified_user.id)

        return {"status": "success",
                "data": result,
                "detail": None
                }

    except InvalidPage:
        raise Errors.invalid_page_number_400

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@feedback_router.get("/get/received", name="feedback:get received feedback", dependencies=[Depends(HTTPBearer())],
                     responses=GET_FEEDBACK_RECEIVED_RESPONSES)
async def get_sent_received(
        verified_user: CurrentUser,
        page: int = Query(gt=0, default=1),
        session: AsyncSession = Depends(get_async_session)):
    try:
        if verified_user.role_id == 1:
            raise UserNotAdminSupervisor

        if page < 1:
            raise InvalidPage

        result = await feedback_received_db(page=page, session=session, user_id=verified_user.id)

        return {"status": "success",
                "data": result,
                "detail": None
                }

    except InvalidPage:
        raise Errors.invalid_page_number_400

    except UserNotAdminSupervisor:
        raise Errors.user_not_allowed_405

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@feedback_router.patch("/patch", name="feedback:patch feedback", dependencies=[Depends(HTTPBearer())],
                       responses=PATCH_FEEDBACK_RESPONSES)
async def patch_feedback(
        edited_feedback: FeedbackUpdate,
        verified_user: CurrentUser,
        feedback_id: int = Query(gt=0),
        session: AsyncSession = Depends(get_async_session)):
    try:
        if edited_feedback.rating not in (1, 2, 3, 4, 5):
            raise RatingException

        feedback_result = await feedback_by_id_db(feedback_id=feedback_id, session=session)

        if not feedback_result:
            raise FeedbackNotFound

        question_result = await get_question_id_db(question_id=feedback_result[0]["question_id"], session=session)

        if not question_result:
            raise QuestionNotFound

        if feedback_result[0]["user_id"] != verified_user.id and verified_user.id != 3:
            raise NotAllowed

        remaining_time = await get_remaining_time(feedback_result[0]["added_at"], target_time=900)
        remaining_time = remaining_time // 60

        if abs(remaining_time) > 15:
            raise FeedbackNotEditable

        for row in feedback_result:
            if row["feedback_title"] == edited_feedback.feedback_title and row["rating"] == edited_feedback.rating:
                returned_object = FeedbackCreate(rating=row["rating"],
                                                 feedback_title=row["feedback_title"],
                                                 user_id=row["user_id"],
                                                 question_id=row["question_id"],
                                                 question_author_id=question_result[0]["question_author_id"]
                                                 )
                return {"status": "success",
                        "data": returned_object,
                        "detail": None
                        }

        feedback_create = FeedbackCreate(rating=edited_feedback.rating,
                                         feedback_title=edited_feedback.feedback_title,
                                         user_id=feedback_result[0]["user_id"],
                                         question_id=feedback_result[0]["question_id"],
                                         question_author_id=question_result[0]["question_author_id"]
                                         )

        stmt = update(feedback).values(**feedback_create.model_dump()).where(feedback.c.id == feedback_id)
        await session.execute(stmt)
        await session.commit()

        return {"status": "success",
                "data": feedback_create,
                "detail": None
                }

    except RatingException:
        raise Errors.rating_mark_400

    except (FeedbackNotFound, QuestionNotFound):
        raise Errors.feedback_not_found_404

    except NotAllowed:
        raise Errors.not_allowed_editing_405

    except FeedbackNotEditable:
        raise Errors.time_editing_elapsed_405

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@feedback_router.delete("/delete", name="feedback:delete feedback",
                        dependencies=[Depends(HTTPBearer())], responses=DELETE_FEEDBACK_RESPONSES)
async def delete_feedback(
        verified_user: CurrentUser,
        feedback_id: int = Query(gt=0),
        session: AsyncSession = Depends(get_async_session)
):
    try:

        feedback_result = await feedback_by_id_db(feedback_id=feedback_id, session=session)

        if not feedback_result:
            raise FeedbackNotFound

        else:
            if feedback_result[0]["user_id"] != verified_user.id and verified_user.id != 3:
                raise NotAllowed

            remaining_time = await get_remaining_time(feedback_result[0]["added_at"], target_time=3600 * 12)
            remaining_time = remaining_time // 3600

            if remaining_time > 0:
                raise NotAllowed

        await delete_feedback_id(feedback_id=feedback_id, session=session)

        return {"status": "success",
                "data": None,
                "detail": None
                }

    except FeedbackNotFound:
        raise Errors.feedback_not_found_404

    except NotAllowed:
        raise Errors.not_allowed_feedback_yourself_405

    except NotAllowedDeleteBeforeTime:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail=f"You can't delete feedback now, please wait {remaining_time} hours")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
