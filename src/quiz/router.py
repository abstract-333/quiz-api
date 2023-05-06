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
from quiz.models import quiz
from quiz.schemas import QuizCreate, QuizRead
from utils.custom_exceptions import DuplicatedQuizException
from utils.error_code import ErrorCode
from utils.result_into_list import ResultIntoList

quiz_router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"],
)

ADD_QUIZ_RESPONSES: OpenAPIResponseType = {
    status.HTTP_403_FORBIDDEN: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {ErrorCode.USER_NOT_ADMIN_SUPERVISOR: {
                    "summary": "Only supervisor or admin can enter quizzes",
                    "value": {"detail": ErrorCode.USER_NOT_ADMIN_SUPERVISOR},
                }
                }
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


@quiz_router.post("/add", name="quiz:add quiz",dependencies=[Depends(HTTPBearer())], responses=ADD_QUIZ_RESPONSES)
async def add_quiz(new_quiz: QuizRead, verified_user: User = Depends(current_user),
                   session: AsyncSession = Depends(get_async_session)) -> dict:
    try:
        if verified_user.role_id == 1:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorCode.USER_NOT_ADMIN_SUPERVISOR)
        query = select(quiz).where(quiz.c.question == new_quiz.question)
        result_proxy = await session.execute(query)
        result = ResultIntoList(result_proxy=result_proxy).parse()  # converting result to list
        for element in result:
            if Counter(element["choices"]) == Counter(new_quiz.choices):  # checking if duplicated
                raise DuplicatedQuizException
        quiz_create = QuizCreate(resolve_time=new_quiz.resolve_time,
                                 question=new_quiz.question,
                                 choices=new_quiz.choices,
                                 answer=new_quiz.answer,
                                 added_by=verified_user.username,
                                 type=new_quiz.type)
        stmt = insert(quiz).values(**quiz_create.dict())
        await session.execute(stmt)
        await session.commit()
        return {"status": "success",
                "data": quiz_create,
                "details": None
                }
    except DuplicatedQuizException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail = ErrorCode.QUIZ_DUPLICATED)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")


@quiz_router.get("/get/", name="quiz: patch quiz", dependencies=[Depends(HTTPBearer())])
async def patch_quiz(edited_quiz: QuizRead, verified_user: User = Depends(current_user),
                     session: AsyncSession = Depends(get_async_session)):

@quiz_router.patch("/patch", name="quiz: patch quiz", dependencies=[Depends(HTTPBearer())])
async def patch_quiz(edited_quiz: QuizRead, verified_user: User = Depends(current_user),
                     session: AsyncSession = Depends(get_async_session)):
    try:
        if verified_user.role_id == 1:
            raise HTTPException(status_code=405, detail={
                "status": "error",
                "data": None,
                "details": "Students can't edit(patch) quizzes"
            })
        query = select(quiz).where(quiz.c.question == edited_quiz.question)
        result_proxy = await session.execute(query)
        result = ResultIntoList(result_proxy=result_proxy).parse()
        for element in result:
            if all([Counter(element["choices"]), element["resolve_time"], element["question"], element["answer"],
                    element["type"]]) == all(
                [Counter(edited_quiz.choices), edited_quiz.resolve_time, edited_quiz.answer, edited_quiz.answer,
                 edited_quiz.type]):
                raise DuplicatedQuizException
        stmt = update(quiz).valaues(**edited_quiz.dict()).where(quiz.c.id == result[0]["id"])
        await session.execute(stmt)
        await session.commit()
        return {"status": "success",
                "data": edited_quiz,
                "details": None
                }
    except DuplicatedQuizException:
        raise HTTPException(status_code=409, detail={
            "status": "error",
            "data": None,
            "details": "Quiz duplicated, you've entered same question with same choices"
        })
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": Exception
        })
