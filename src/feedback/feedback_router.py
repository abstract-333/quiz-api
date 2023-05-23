from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from auth.base_config import current_user
from auth.auth_models import User
from database import get_async_session
from feedback.feedback_docs import ADD_FEEDBACK_QUESTION_RESPONSES, GET_FEEDBACK_SENT_RESPONSES, \
    PATCH_FEEDBACK_QUESTION_RESPONSES
from feedback.feedback_db import feedback_sent_db, feedback_received_db, feedback_by_id_db, \
    feedback_question_id_user_id_db, delete_feedback_id, get_remaining_time
from feedback.feedback_models import feedback
from feedback.feedback_schemas import FeedbackRead, FeedbackUpdate, FeedbackCreate
from question.question_db import get_question_id_db
from utils.custom_exceptions import FeedbackAlreadySent, QuestionNotExists, RatingException, DuplicatedTitle, \
    InvalidPage, FeedbackNotExists, FeedbackNotEditable, UserNotAdminSupervisor, NotAllowedDeleteBeforeTime, NotAllowed
from utils.error_code import ErrorCode

feedback_router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
)


@feedback_router.post("/add", name="feedback:add feedback", dependencies=[Depends(HTTPBearer())],
                      responses=ADD_FEEDBACK_QUESTION_RESPONSES)
async def add_feedback(added_feedback: FeedbackRead, verified_user: User = Depends(current_user),
                       session: AsyncSession = Depends(get_async_session)):
    try:

        if added_feedback.rating not in (1, 2, 3, 4, 5):
            raise RatingException

        result_question = await get_question_id_db(question_id=added_feedback.question_id, session=session)

        if not result_question:
            raise QuestionNotExists

        else:
            if result_question[0]["added_by"] != verified_user.id:
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

    except NotAllowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorCode.NOT_ALLOWED_FEEDBACK_YOURSELF)

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

        result = await feedback_sent_db(page=page, session=session, user_id=verified_user.id)

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
async def get_sent_received(page: int = 1, verified_user: User = Depends(current_user),
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

    except UserNotAdminSupervisor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorCode.USER_NOT_ADMIN_SUPERVISOR)

    except InvalidPage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.INVALID_PAGE)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@feedback_router.patch("/patch", name="feedback:patch feedback", dependencies=[Depends(HTTPBearer())],
                       responses=PATCH_FEEDBACK_QUESTION_RESPONSES)
async def patch_feedback(feedback_id: int, edited_feedback: FeedbackUpdate, verified_user: User = Depends(current_user),
                         session: AsyncSession = Depends(get_async_session)):
    try:
        if edited_feedback.rating not in (1, 2, 3, 4, 5):
            raise RatingException

        result = await feedback_by_id_db(feedback_id=feedback_id, session=session)

        if not result:
            raise FeedbackNotExists

        question_result = await get_question_id_db(question_id=result[0]["question_id"], session=session)

        if not question_result:
            raise QuestionNotExists

        if result[0]["user_id"] != verified_user.id and verified_user.id != 3:
            raise NotAllowed

        remaining_time = await get_remaining_time(result[0]["added_at"], target_time=900)
        remaining_time = remaining_time // 60

        if abs(remaining_time) > 15:
            raise FeedbackNotEditable

        for row in result:
            if row["feedback_title"] == edited_feedback.feedback_title and row["rating"] == edited_feedback.rating:
                returned_object = FeedbackCreate(rating=row["rating"],
                                                 feedback_title=row["feedback_title"],
                                                 user_id=row["user_id"],
                                                 question_id=row["question_id"],
                                                 question_author_id=question_result[0]["question_author_id"]
                                                 )
                return {"status": "success",
                        "data": "returned_object",
                        "detail": None
                        }

        feedback_create = FeedbackCreate(rating=edited_feedback.rating,
                                         feedback_title=edited_feedback.feedback_title,
                                         user_id=result[0]["user_id"],
                                         question_id=result[0]["question_id"],
                                         question_author_id=question_result[0]["question_author_id"]
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

    except (FeedbackNotExists, QuestionNotExists):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorCode.FEEDBACK_NOT_EXISTS)

    except NotAllowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorCode.NOT_ALLOWED_PATCH_FEEDBACK)

    except FeedbackNotEditable:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail="You can edit the feedback for 15 minutes after you sent it")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@feedback_router.delete("/{feedback_id}", name="feedback:delete feedback",
                        dependencies=[Depends(HTTPBearer())], )
async def delete_feedback(feedback_id: int, verified_user: User = Depends(current_user),
                          session: AsyncSession = Depends(get_async_session)):
    try:

        result = await feedback_by_id_db(feedback_id=feedback_id, session=session)

        if not result:
            raise FeedbackNotExists

        else:
            if result[0]["user_id"] != verified_user.id and verified_user.id != 3:
                raise NotAllowed

            remaining_time = await get_remaining_time(result[0]["added_at"], target_time=3600 * 12)
            remaining_time = remaining_time // 3600

            if remaining_time > 0:
                raise NotAllowed

        await delete_feedback_id(feedback_id=feedback_id, session=session)

        return {"status": "success",
                "data": None,
                "detail": None
                }

    except FeedbackNotExists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorCode.FEEDBACK_NOT_EXISTS)

    except NotAllowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorCode.NOT_ALLOWED_FEEDBACK_YOURSELF)

    except NotAllowedDeleteBeforeTime:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail=f"You can't delete feedback now, please wait {remaining_time} hours")

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
