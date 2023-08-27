from fastapi import APIRouter, Depends, HTTPException, FastAPI, Query
from fastapi.security import HTTPBearer
from numpy import random as num_random
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from api.quiz.quiz_db import get_quiz_db
from api.quiz.quiz_docs import GET_QUIZ_RESPONSES
from api.quiz.quiz_errors import Errors
from core.dependecies import CurrentUser, Session
from utilties.custom_exceptions import QuestionsInvalidNumber, EmptyList

quiz_app = FastAPI()
quiz_router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"]
)


@quiz_router.get(
    path="/get",
    name="quiz:get quiz",
    dependencies=[Depends(HTTPBearer())], responses=GET_QUIZ_RESPONSES
)
async def get_quiz(
        request: Request,
        response: Response,
        verified_user: CurrentUser,
        session: Session,
        number_questions: int = Query(default=50, lt=51, gt=19),
) -> dict:
    try:
        # Check if number of questions requested is valid
        if number_questions not in range(20, 51):
            raise QuestionsInvalidNumber

        # Get questions from db
        number_software_questions = int(number_questions * 0.6)
        number_network_questions = int(number_questions * 0.2)
        number_ai_questions = int(number_questions * 0.2)

        if verified_user.role_id != 1:
            # Check if user id admin_panel or supervisor to validate that we don't give them their questions in quiz
            result = await get_quiz_db(number_ai_questions=number_ai_questions,
                                       number_network_questions=number_network_questions,
                                       number_software_questions=number_software_questions,
                                       user_id=verified_user.id,
                                       session=session)

        else:
            # Get quiz for user(student)
            result = await get_quiz_db(number_ai_questions=number_ai_questions,
                                       number_network_questions=number_network_questions,
                                       number_software_questions=number_software_questions,
                                       session=session)

        # Raise exception if list is empty
        if not result:
            raise EmptyList

        # Shuffle the list before return it
        num_random.shuffle(result)

        return {"status": "success",
                "data": result,
                "details": None
                }

    except EmptyList:
        raise Errors.empty_list_returned_404

    except QuestionsInvalidNumber:
        raise Errors.number_of_requested_questions_invalid_400

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
