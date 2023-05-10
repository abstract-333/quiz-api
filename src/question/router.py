from collections import Counter
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from auth.base_config import current_user
from auth.models import User
from database import get_async_session
from question.models import question
from question.schemas import QuizCreate, QuizRead
from section.models import section
from utils.custom_exceptions import DuplicatedQuizException, UserNotAdminSupervisor
from utils.error_code import ErrorCode
from utils.result_into_list import ResultIntoList

question_router = APIRouter(
    prefix="/question",
    tags=["Question"],
)

ADD_QUESTION_RESPONSES: OpenAPIResponseType = {
    status.HTTP_403_FORBIDDEN: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.USER_NOT_ADMIN_SUPERVISOR: {
                    "summary": "Only supervisor or admin can enter quizzes",
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


@question_router.post("/add", name="question:add question", dependencies=[Depends(HTTPBearer())],
                      responses=ADD_QUESTION_RESPONSES)
async def add_question(new_quiz: QuizRead, verified_user: User = Depends(current_user),
                       session: AsyncSession = Depends(get_async_session)) -> dict:
    try:
        if verified_user.role_id == 1:
            raise UserNotAdminSupervisor
        query = select(question).where(question.c.question_title == new_quiz.question_title)
        result_proxy = await session.execute(query)
        result = ResultIntoList(result_proxy=result_proxy).parse()  # converting result to list
        for element in result:
            if Counter(element["choices"]) == Counter(new_quiz.choices):  # checking if duplicated
                raise DuplicatedQuizException
        quiz_create = QuizCreate(resolve_time=new_quiz.resolve_time,
                                 question_title=new_quiz.question_title,
                                 choices=new_quiz.choices,
                                 answer=new_quiz.answer,
                                 added_by=verified_user.username,
                                 section_id=new_quiz.section_id)
        stmt = insert(question).values(**quiz_create.dict())
        await session.execute(stmt)
        await session.commit()
        return {"status": "success",
                "data": quiz_create,
                "detail": None
                }
    except UserNotAdminSupervisor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorCode.USER_NOT_ADMIN_SUPERVISOR)
    except DuplicatedQuizException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ErrorCode.QUIZ_DUPLICATED)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@question_router.get("/get/me", name="question:get question-mine", dependencies=[Depends(HTTPBearer())],
                     responses=GET_QUESTION_RESPONSES)
async def get_question_me(offset: int = 0, session: AsyncSession = Depends(get_async_session),
                          verified_user: User = Depends(current_user)) -> dict:
    try:
        query = select(question).where(question.c.added_by == verified_user.username).offset(offset).limit(10)
        result_proxy = await session.execute(query)
        result = ResultIntoList(result_proxy=result_proxy).parse()
        return {"status": "success",
                "data": result,
                "detail": None}
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@question_router.get("/get/{section_id}", name="question:get question", dependencies=[Depends(HTTPBearer())],
                     responses=GET_QUESTION_RESPONSES)
async def get_question_section_id(section_id: int, offset: int = 0,
                                  session: AsyncSession = Depends(get_async_session)) -> dict:
    try:
        section_name_query = select(section.name).where(section.c.id == section_id)
        section_name = await session.execute(section_name_query)
        question_list_query = select(section_name).where(question.c.section_id == section_id).offset(offset).limit(10)
        result_proxy = await session.execute(question_list_query)
        result = ResultIntoList(result_proxy=result_proxy).parse()
        return {"status": "success",
                "data": result,
                "detail": None}
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)

# @question_router.patch("/patch", name="question: patch question", dependencies=[Depends(HTTPBearer())])
# async def patch_question(edited_quiz: QuizRead, verified_user: User = Depends(current_user),
#                          session: AsyncSession = Depends(get_async_session)):
#     try:
#         if verified_user.role_id == 1:
#             raise HTTPException(status_code=405, detail={
#                 "status": "error",
#                 "data": None,
#                 "details": "Students can't edit(patch) quizzes"
#             })
#         query = select(question).where(question.c.question == edited_quiz.question)
#         result_proxy = await session.execute(query)
#         result = ResultIntoList(result_proxy=result_proxy).parse()
#         for element in result:
#             if all([Counter(element["choices"]), element["resolve_time"], element["question"], element["answer"],
#                     element["type"]]) == all(
#                 [Counter(edited_quiz.choices), edited_quiz.resolve_time, edited_quiz.answer, edited_quiz.answer,
#                  edited_quiz.type]):
#                 raise DuplicatedQuizException
#         stmt = update(question).valaues(**edited_quiz.dict()).where(question.c.id == result[0]["id"])
#         await session.execute(stmt)
#         await session.commit()
#         return {"status": "success",
#                 "data": edited_quiz,
#                 "details": None
#                 }
#     except DuplicatedQuizException:
#         raise HTTPException(status_code=409, detail={
#             "status": "error",
#             "data": None,
#             "details": "Quiz duplicated, you've entered same question with same choices"
#         })
#     except Exception:
#         raise HTTPException(status_code=500, detail={
#             "status": "error",
#             "data": None,
#             "details": Exception
#         })
