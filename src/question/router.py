import itertools
from collections import Counter
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
from question.models import QUESTIONS_SECTIONS
from question.schemas import QuestionCreate, QuestionRead
from utils.custom_exceptions import DuplicatedQuestionException, UserNotAdminSupervisor, OutOfSectionIdException, \
    AnswerNotIncluded, NumberOfChoicesNotFour
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
                "examples": {ErrorCode.QUIZ_DUPLICATED: {
                    "summary": "Quiz duplicated, you've entered same question with same choices and answer",
                    "value": {"detail": ErrorCode.QUIZ_DUPLICATED},
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
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.OUT_OF_SECTION_ID: {
                    "summary": "Not authenticated",
                    "value": {"detail": ErrorCode.OUT_OF_SECTION_ID},
                }}
            },
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal sever error.",
    }
}


async def checking_question_validity(added_quiz, verified_user):
    added_quiz.choices.discard('')  # removing empty string from set

    if verified_user.role_id == 1:  # user can't add questions
        raise UserNotAdminSupervisor

    if len(added_quiz.choices) != 4:  # checking if question have 4 choices
        raise NumberOfChoicesNotFour

    if added_quiz.answer not in added_quiz.choices:  # checking if answer included in choices
        raise AnswerNotIncluded


@question_router.post("/add", name="question:add question", dependencies=[Depends(HTTPBearer())],
                      responses=ADD_PATCH_QUESTION_RESPONSES)
async def add_question(added_question: QuestionRead, verified_user: User = Depends(current_user),
                       session: AsyncSession = Depends(get_async_session)) -> dict:
    try:
        await checking_question_validity(added_question, verified_user)

        table = QUESTIONS_SECTIONS[verified_user.section_id - 1]
        query = select(table).where(table.c.question_title == added_question.question_title)
        result_proxy = await session.execute(query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))  # converting result to list

        for element in result:
            # checking if duplicated
            if (Counter(element["choices"]), element["question_title"]) == (Counter(added_question.choices),
                                                                            added_question.question_title):
                raise DuplicatedQuestionException
        question_create = QuestionCreate(resolve_time=added_question.resolve_time,
                                         question_title=added_question.question_title,
                                         choices=list(added_question.choices),
                                         answer=added_question.answer,
                                         added_by=verified_user.username,
                                         )
        stmt = insert(table).values(**question_create.dict())
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
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ErrorCode.QUIZ_DUPLICATED)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@question_router.get("/me", name="question:get question-mine", dependencies=[Depends(HTTPBearer())],
                     responses=GET_QUESTION_RESPONSES)
async def get_question_me(offset: int = 0, session: AsyncSession = Depends(get_async_session),
                          verified_user: User = Depends(current_user)) -> dict:
    try:
        table = QUESTIONS_SECTIONS[verified_user.section_id - 1]
        query = select(table).where(table.c.added_by == verified_user.username).offset(offset).limit(10)

        result_proxy = await session.execute(query)
        result = ResultIntoList(result_proxy=result_proxy)

        result = list(itertools.chain(result.parse()))
        return {"status": "success",
                "data": result,
                "detail": None}
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@question_router.get("/{section_id}", name="question:get question", dependencies=[Depends(HTTPBearer())],
                     responses=GET_QUESTION_SECTION_RESPONSES)
async def get_question_section_id(section_id: int, offset: int = 0,
                                  session: AsyncSession = Depends(get_async_session)) -> dict:
    try:
        if section_id not in (1, 2, 3):
            raise OutOfSectionIdException

        table = QUESTIONS_SECTIONS[section_id - 1]
        question_list_query = select(table).offset(offset).limit(10)
        result_proxy = await session.execute(question_list_query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        return {"status": "success",
                "data": result,
                "detail": None}
    except OutOfSectionIdException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.OUT_OF_SECTION_ID)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@question_router.patch("/patch", name="question: patch question", dependencies=[Depends(HTTPBearer())],
                       responses=ADD_PATCH_QUESTION_RESPONSES)
async def patch_question(question_id: int, edited_question: QuestionRead, verified_user: User = Depends(current_user),
                         session: AsyncSession = Depends(get_async_session)):
    try:
        table = QUESTIONS_SECTIONS[verified_user.section_id - 1]

        await checking_question_validity(edited_question, verified_user)

        query = select(table).where(table.c.id == question_id)
        result_proxy = await session.execute(query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        for element in result:
            if (Counter(element["choices"]), element["resolve_time"], element["question_title"], element["answer"]) == (
                    Counter(edited_question.choices), edited_question.resolve_time, edited_question.question_title,
                    edited_question.answer):
                return {"status": "success",
                        "data": edited_question,
                        "details": None
                        }

        query = select(table).where(table.c.question_title == edited_question.question_title and
                                    table.c.id != question_id)
        result_proxy = await session.execute(query)

        result = ResultIntoList(result_proxy=result_proxy)
        result = list(itertools.chain(result.parse()))

        for element in result:
            if (Counter(element["choices"]), element["resolve_time"], element["question_title"], element["answer"]) == (
                    Counter(edited_question.choices), edited_question.resolve_time, edited_question.question_title,
                    edited_question.answer):
                raise DuplicatedQuestionException

        question_update = QuestionCreate(resolve_time=edited_question.resolve_time,
                                         question_title=edited_question.question_title,
                                         choices=list(edited_question.choices),
                                         answer=edited_question.answer,
                                         added_by=verified_user.username,
                                         )
        stmt = update(table).values(**question_update.dict()).where(table.c.id == question_id)
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
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ErrorCode.QUIZ_DUPLICATED)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
