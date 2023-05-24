from collections import Counter
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from auth.base_config import current_user
from auth.auth_models import User
from database import get_async_session
from feedback.feedback_db import check_feedback_question_id, delete_feedback_question_id
from question.question_docs import ADD_QUESTION_RESPONSES, GET_QUESTION_RESPONSES, GET_QUESTION_SECTION_RESPONSES, \
    PATCH_QUESTION_RESPONSES, DELETE_QUESTION_RESPONSES
from question.question_schemas import QuestionCreate, QuestionRead, QuestionUpdate
from question.question_db import get_questions_id_db, get_questions_section_db, check_question_validity, \
    get_questions_title_db, update_question_db, get_question_id_db, get_questions_duplicated_db, insert_question_db, \
    delete_question_db
from utils.custom_exceptions import DuplicatedQuestionException, UserNotAdminSupervisor, OutOfSectionIdException, \
    AnswerNotIncluded, NumberOfChoicesNotFour, InvalidPage, QuestionNotExists, NotAllowed
from utils.error_code import ErrorCode

question_router = APIRouter(
    prefix="/question",
    tags=["Question"],
)


@question_router.post("/add", name="question:add question", dependencies=[Depends(HTTPBearer())],
                      responses=ADD_QUESTION_RESPONSES)
async def add_question(added_question: QuestionRead, verified_user: User = Depends(current_user),
                       session: AsyncSession = Depends(get_async_session)) -> dict:
    try:

        await check_question_validity(received_question=added_question, role_id=verified_user.role_id)

        questions_with_same_title = await get_questions_title_db(question_title=added_question.question_title,
                                                                 session=session)

        for element in questions_with_same_title:
            # checking if duplicated
            if (Counter(element["choices"]), element["question_title"]) == (Counter(added_question.choices),
                                                                            added_question.question_title):
                raise DuplicatedQuestionException

        question_create = QuestionCreate(question_title=added_question.question_title,
                                         choices=list(added_question.choices),  # converting set to list
                                         answer=added_question.answer,
                                         added_by=verified_user.id,
                                         section_id=verified_user.section_id
                                         )

        await insert_question_db(question_create, session)

        return {"status": "success",
                "data": question_create,
                "detail": None
                }

    except NumberOfChoicesNotFour:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.NUMBER_OF_CHOICES_NOT_FOUR)

    except AnswerNotIncluded:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.ANSWER_NOT_INCLUDED_IN_CHOICES)

    except UserNotAdminSupervisor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorCode.USER_NOT_ADMIN_SUPERVISOR)

    except DuplicatedQuestionException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ErrorCode.QUESTION_DUPLICATED)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@question_router.get("/me", name="question:get question-mine", dependencies=[Depends(HTTPBearer())],
                     responses=GET_QUESTION_RESPONSES)
async def get_question_me(page: int = 1, session: AsyncSession = Depends(get_async_session),
                          verified_user: User = Depends(current_user)) -> dict:
    try:
        if page < 1:
            raise InvalidPage

        result = await get_questions_id_db(page=page, session=session, user_id=verified_user.id)

        return {"status": "success",
                "data": result,
                "detail": None}
    except InvalidPage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.INVALID_PAGE)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@question_router.get("/get", name="question:get question", dependencies=[Depends(HTTPBearer())],
                     responses=GET_QUESTION_SECTION_RESPONSES)
async def get_question_section_id(section_id: int, page: int = 1,
                                  session: AsyncSession = Depends(get_async_session)) -> dict:
    try:
        if page < 1:
            raise InvalidPage

        if section_id not in (1, 2, 3):
            raise OutOfSectionIdException

        result = await get_questions_section_db(page=page, section_id=section_id, session=session)

        return {"status": "success",
                "data": result,
                "detail": None}

    except InvalidPage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.INVALID_PAGE)

    except OutOfSectionIdException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.OUT_OF_SECTION_ID)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@question_router.patch("/patch", name="question: patch question", dependencies=[Depends(HTTPBearer())],
                       responses=PATCH_QUESTION_RESPONSES)
async def patch_question(question_id: int, edited_question: QuestionRead, verified_user: User = Depends(current_user),
                         session: AsyncSession = Depends(get_async_session)) -> dict:
    try:

        await check_question_validity(edited_question, verified_user)

        question_old = await get_question_id_db(question_id=question_id, session=session)

        if not question_old:
            raise QuestionNotExists

        if question_old[0]["added_by"] != verified_user.id and verified_user.role_id != 3:
            raise NotAllowed

        if (Counter(question_old[0]["choices"]), question_old[0]["question_title"], question_old[0]["answer"]) == (
                Counter(edited_question.choices), edited_question.question_title,
                edited_question.answer):
            return {"status": "success",
                    "data": edited_question,
                    "details": None
                    }

        result = await get_questions_duplicated_db(question_title=edited_question.question_title,
                                                   question_id=question_id,
                                                   session=session)

        for element in result:
            if (Counter(element["choices"]), element["question_title"], element["answer"]) == (
                    Counter(edited_question.choices), edited_question.question_title,
                    edited_question.answer):
                raise DuplicatedQuestionException

        question_update = QuestionUpdate(question_title=edited_question.question_title,
                                         choices=list(edited_question.choices),
                                         answer=edited_question.answer,
                                         )
        await update_question_db(question_id=question_id, question_update=question_update, session=session)

        return {"status": "success",
                "data": edited_question,
                "details": None
                }

    except NumberOfChoicesNotFour:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.NUMBER_OF_CHOICES_NOT_FOUR)

    except AnswerNotIncluded:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.ANSWER_NOT_INCLUDED_IN_CHOICES)

    except NotAllowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorCode.NOT_QUESTION_OWNER)
    
    except UserNotAdminSupervisor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorCode.USER_NOT_ADMIN_SUPERVISOR)

    except QuestionNotExists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorCode.QUESTION_NOT_EXISTS)

    except DuplicatedQuestionException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ErrorCode.QUESTION_DUPLICATED)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@question_router.delete("/delete", name="question: delete question", dependencies=[Depends(HTTPBearer())],
                        responses=DELETE_QUESTION_RESPONSES)
async def delete_question(question_id: int, verified_user: User = Depends(current_user),
                          session: AsyncSession = Depends(get_async_session)) -> dict:
    try:

        check_feedback = await check_feedback_question_id(question_id=question_id, session=session)

        question_for_deleting = await get_question_id_db(question_id=question_id, session=session)

        if question_for_deleting[0]["added_by"] != verified_user.id:
            raise NotAllowed

        if not question_for_deleting:
            raise QuestionNotExists

        if check_feedback:
            await delete_feedback_question_id(question_id=question_id, session=session)

        await delete_question_db(question_id=question_id, session=session)

        return {"status": "success",
                "data": None,
                "details": None
                }

    except NotAllowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorCode.NOT_QUESTION_OWNER)

    except QuestionNotExists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorCode.QUESTION_NOT_EXISTS)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
