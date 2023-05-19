import itertools
from collections import Counter
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from sqlalchemy import insert, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from auth.base_config import current_user
from auth.models import User, user
from database import get_async_session
from feedback.models import feedback
from question.models import question
from question.schemas import QuestionCreate, QuestionRead
from question.fuctions import get_questions, get_questions_section, checking_question_validity, get_questions_title
from utils.custom_exceptions import DuplicatedQuestionException, UserNotAdminSupervisor, OutOfSectionIdException, \
    AnswerNotIncluded, NumberOfChoicesNotFour, InvalidPage
from utils.error_code import ErrorCode
from utils.result_into_list import ResultIntoList

question_router = APIRouter(
    prefix="/question",
    tags=["Question"],
)

ADD_PATCH_QUESTION_RESPONSES: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.ANSWER_NOT_INCLUDED_IN_CHOICES: {
                    "summary": "Not valid question formula",
                    "value": {"detail": ErrorCode.ANSWER_NOT_INCLUDED_IN_CHOICES},
                },
                    ErrorCode.NUMBER_OF_CHOICES_NOT_FOUR: {
                        "summary": "Number of choices not equal to four",
                        "value": {"detail": ErrorCode.NUMBER_OF_CHOICES_NOT_FOUR},
                    },
                }
            },
        },
    },
    status.HTTP_403_FORBIDDEN: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.USER_NOT_ADMIN_SUPERVISOR: {
                    "summary": "Only supervisor or admin can enter or patch quizzes",
                    "value": {"detail": ErrorCode.USER_NOT_ADMIN_SUPERVISOR},
                }, ErrorCode.USER_NOT_AUTHENTICATED: {
                    "summary": "Not authenticated",
                    "value": {"detail": "Not authenticated"},
                }}
            },
        },
    },
    status.HTTP_409_CONFLICT: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.QUESTION_DUPLICATED: {
                    "summary": "Quiz duplicated, you've entered same question with same choices and answer",
                    "value": {"detail": ErrorCode.QUESTION_DUPLICATED},
                }
                }
            }
        }
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal sever error.",
    }
}

GET_QUESTION_RESPONSES: OpenAPIResponseType = {
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
                "examples": {ErrorCode.USER_NOT_AUTHENTICATED: {
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

GET_QUESTION_SECTION_RESPONSES: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.OUT_OF_SECTION_ID: {
                    "summary": "Not authenticated",
                    "value": {"detail": ErrorCode.OUT_OF_SECTION_ID},
                },
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
                "examples": {ErrorCode.USER_NOT_AUTHENTICATED: {
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


@question_router.post("/add", name="question:add question", dependencies=[Depends(HTTPBearer())],
                      responses=ADD_PATCH_QUESTION_RESPONSES)
async def add_question(added_question: QuestionRead, verified_user: User = Depends(current_user),
                       session: AsyncSession = Depends(get_async_session)) -> dict:
    try:
        await checking_question_validity(received_question=added_question, role_id=verified_user.role_id)

        questions_same_question_title = await get_questions_title(question_title=added_question.question_title, session=session)

        for element in questions_same_question_title:
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

        stmt = insert(question).values(**question_create.dict())
        await session.execute(stmt)
        await session.commit()

        return {"status": "success",
                "data": question_create,
                "detail": None
                }

    except UserNotAdminSupervisor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorCode.USER_NOT_ADMIN_SUPERVISOR)

    except NumberOfChoicesNotFour:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.NUMBER_OF_CHOICES_NOT_FOUR)

    except AnswerNotIncluded:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.ANSWER_NOT_INCLUDED_IN_CHOICES)

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

        result = await get_questions(page=page, session=session, user_id=verified_user.id)

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

        result = await get_questions_section(page=page, section_id=section_id, session=session)

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
                       responses=ADD_PATCH_QUESTION_RESPONSES)
async def patch_question(question_id: int, edited_question: QuestionRead, verified_user: User = Depends(current_user),
                         session: AsyncSession = Depends(get_async_session)) -> dict:
    try:

        await checking_question_validity(edited_question, verified_user)

        query = select(question).where(question.c.id == question_id)
        result_proxy = await session.execute(query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        if (Counter(result["choices"]), result["question_title"], result["answer"]) == (
                Counter(edited_question.choices), edited_question.question_title,
                edited_question.answer):
            return {"status": "success",
                    "data": edited_question,
                    "details": None
                    }

        query = select(question).where(question.c.question_title == edited_question.question_title and
                                       question.c.id != question_id)
        result_proxy = await session.execute(query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        for element in result:
            if (Counter(element["choices"]), element["question_title"], element["answer"]) == (
                    Counter(edited_question.choices), edited_question.question_title,
                    edited_question.answer):
                raise DuplicatedQuestionException

        question_update = QuestionCreate(question_title=edited_question.question_title,
                                         choices=list(edited_question.choices),
                                         answer=edited_question.answer,
                                         added_by=verified_user.id,
                                         section_id=verified_user.section_id
                                         )

        stmt = update(question).values(**question_update.dict()).where(question.c.id == question_id)
        await session.execute(stmt)
        await session.commit()

        return {"status": "success",
                "data": edited_question,
                "details": None
                }

    except UserNotAdminSupervisor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorCode.USER_NOT_ADMIN_SUPERVISOR)

    except NumberOfChoicesNotFour:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.NUMBER_OF_CHOICES_NOT_FOUR)

    except AnswerNotIncluded:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.ANSWER_NOT_INCLUDED_IN_CHOICES)

    except DuplicatedQuestionException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ErrorCode.QUESTION_DUPLICATED)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
