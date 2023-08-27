from collections import Counter
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from starlette import status

from api.auth.base_config import current_superuser
from api.feedback.feedback_db import (
    check_feedback_question_id,
    delete_feedback_question_id,
    get_remaining_time
)
from api.question.question_db import (
    get_questions_id_db,
    get_questions_section_db,
    get_questions_title_db,
    update_question_db,
    get_question_id_db,
    insert_question_db,
    delete_question_db,
    get_question_ref,
    update_question_active_db
)
from api.question.question_docs import (
    ADD_QUESTION_RESPONSES,
    GET_QUESTION_RESPONSES,
    GET_QUESTION_SECTION_RESPONSES,
    PATCH_QUESTION_RESPONSES,
    DELETE_QUESTION_RESPONSES
)
from api.question.question_errors import Errors as QuestionErrors
from api.question.question_schemas import QuestionCreate, QuestionRead, QuestionUpdate
from api.rating.rating_docs import SERVER_ERROR_AUTHORIZED_RESPONSE
from api.section.section_errors import Errors as SectionErrors
from api.section.section_service import SectionService
from core.dependecies import UOWDep, CurrentUser, Session
from utilties.custom_exceptions import (
    DuplicatedQuestionException,
    UserNotAdminSupervisor,
    OutOfSectionIdException,
    AnswerNotIncluded,
    NumberOfChoicesNotFour,
    InvalidPage,
    QuestionNotFound,
    NotAllowed,
    QuestionNotEditable
)

question_router = APIRouter(
    prefix="/question",
    tags=["Question"],
)


async def check_question_validity_user_grants(received_question: QuestionRead, role_id: int):
    received_question.choices.discard('')  # removing empty string from set

    if role_id == 1:  # user can't add questions
        raise UserNotAdminSupervisor

    if len(received_question.choices) != 4:  # checking if question have 4 choices
        raise NumberOfChoicesNotFour

    if received_question.answer not in received_question.choices:  # checking if answer included in choices
        raise AnswerNotIncluded


@question_router.post("/add", name="question:add question", dependencies=[Depends(HTTPBearer())],
                      responses=ADD_QUESTION_RESPONSES)
async def add_question(
        added_question: QuestionRead,
        verified_user: CurrentUser,
        session: Session
) -> dict:
    try:

        await check_question_validity_user_grants(received_question=added_question, role_id=verified_user.role_id)

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
                                         reference=added_question.reference,
                                         reference_link=added_question.reference_link,
                                         added_by=verified_user.id,
                                         section_id=verified_user.section_id
                                         )

        await insert_question_db(question_create, session)

        return {"status": "success",
                "data": question_create,
                "detail": None
                }

    except NumberOfChoicesNotFour:
        raise QuestionErrors.number_choices_not_four_400

    except AnswerNotIncluded:
        raise QuestionErrors.answer_not_included_choices_400

    except UserNotAdminSupervisor:
        raise QuestionErrors.user_not_allowed_405

    except DuplicatedQuestionException:
        raise QuestionErrors.duplicated_question_409

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@question_router.get("/me", name="question:get question-mine", dependencies=[Depends(HTTPBearer())],
                     responses=GET_QUESTION_RESPONSES)
async def get_question_me(
        verified_user: CurrentUser,
        session: Session,
        page: int = Query(gt=0, default=1),
) -> dict:
    try:
        if page < 1:
            raise InvalidPage

        result = await get_questions_id_db(page=page, session=session, user_id=verified_user.id)

        return {"status": "success",
                "data": result,
                "detail": None}

    except InvalidPage:
        raise QuestionErrors.invalid_page_number_400

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@question_router.get("/get", name="question:get question", dependencies=[Depends(HTTPBearer())],
                     responses=GET_QUESTION_SECTION_RESPONSES)
async def get_question_section_id(
        uow: UOWDep,
        verified_user: CurrentUser,
        session: Session,
        section_id: int = Query(gt=0),
        page: int = Query(gt=0, default=1),
) -> dict:
    try:
        if page < 1:
            raise InvalidPage

        await SectionService().get_section_by_id(uow=uow, section_id=section_id)

        if verified_user.role_id == 3:
            # If user is admin_panel then return all question(active or not)
            result = await get_questions_section_db(
                show_inactive=True,
                page=page,
                section_id=section_id,
                session=session
            )
        else:
            # If user is not admin_panel then return just active questions
            result = await get_questions_section_db(
                show_inactive=False,
                page=page,
                section_id=section_id,
                session=session
            )

        return {"status": "success",
                "data": result,
                "detail": None}

    except InvalidPage:
        raise QuestionErrors.invalid_page_number_400

    except OutOfSectionIdException:
        raise SectionErrors.invalid_section_400

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@question_router.patch("/patch", name="question: patch question", dependencies=[Depends(HTTPBearer())],
                       responses=PATCH_QUESTION_RESPONSES)
async def patch_question(
        edited_question: QuestionRead,
        session: Session,
        verified_user: CurrentUser,
        question_id: int = Query(gt=0),
) -> dict:
    try:

        await check_question_validity_user_grants(edited_question, verified_user.role_id)

        question_old = await get_question_id_db(question_id=question_id, session=session)

        if not question_old:
            raise QuestionNotFound

        if question_old[0]["added_by"] != verified_user.id and verified_user.role_id != 3:
            raise NotAllowed

        remaining_time = await get_remaining_time(question_old[0]["added_at"], target_time=1800)
        remaining_time = remaining_time // 60

        if verified_user.role_id == 2:
            del edited_question.active
            if abs(remaining_time) > 15:
                raise QuestionNotEditable

        question_update = QuestionUpdate(question_title=edited_question.question_title,
                                         choices=list(edited_question.choices),
                                         answer=edited_question.answer,
                                         reference=edited_question.reference,
                                         reference_link=edited_question.reference_link,
                                         active=edited_question.active
                                         )

        await update_question_db(question_id=question_id, question_update=question_update, session=session)

        return {"status": "success",
                "data": edited_question,
                "details": None
                }

    except NumberOfChoicesNotFour:
        raise QuestionErrors.number_choices_not_four_400

    except AnswerNotIncluded:
        raise QuestionErrors.answer_not_included_choices_400

    except QuestionNotFound:
        raise QuestionErrors.question_not_found_404

    except NotAllowed:
        raise QuestionErrors.not_question_owner_405

    except UserNotAdminSupervisor:
        raise QuestionErrors.user_not_allowed_405

    except QuestionNotEditable:
        raise QuestionErrors.question_not_editable_405

    except DuplicatedQuestionException:
        raise QuestionErrors.duplicated_question_409

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@question_router.post("/wrong_solved/ref", name="question: get reference", dependencies=[Depends(HTTPBearer())],
                      responses=SERVER_ERROR_AUTHORIZED_RESPONSE)
async def get_wrong_solved(
        verified_user: CurrentUser,
        list_question_id: list[int],
        session: Session) -> dict:
    try:

        questions = await get_question_ref(list_questions=list_question_id, session=session)

        return {"status": "success",
                "data": questions,
                "details": None
                }

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@question_router.post(
    path="/deactivate",
    name="question: make question inactive",
    dependencies=[Depends(HTTPBearer())],
    responses=DELETE_QUESTION_RESPONSES
)
async def make_question_inactive(
        verified_user: CurrentUser,
        session: Session,
        question_id: int = Query(gt=0),
) -> dict:
    try:

        question_processed = await get_question_id_db(question_id=question_id, session=session)

        if not question_processed:
            raise QuestionNotFound

        await update_question_active_db(
            question_id=question_id,
            session=session
        )

        return {"status": "success",
                "data": None,
                "details": None
                }

    except QuestionNotFound:
        raise QuestionErrors.question_not_found_404

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@question_router.delete(
    path="/delete",
    name="question: delete question",
    dependencies=[Depends(HTTPBearer()), Depends(current_superuser)],
    responses=DELETE_QUESTION_RESPONSES
)
async def delete_question(
        session: Session,
        question_id: int = Query(gt=0),
) -> dict:
    try:

        check_feedback = await check_feedback_question_id(question_id=question_id, session=session)

        question_for_deleting = await get_question_id_db(question_id=question_id, session=session)

        if not question_for_deleting:
            raise QuestionNotFound

        if check_feedback:
            await delete_feedback_question_id(question_id=question_id, session=session)

        await delete_question_db(question_id=question_id, session=session)

        return {"status": "success",
                "data": None,
                "details": None
                }

    except QuestionNotFound:
        raise QuestionErrors.question_not_found_404

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)
