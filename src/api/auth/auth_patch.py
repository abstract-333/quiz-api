from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, Query
from fastapi_users import exceptions, schemas
from fastapi_users.manager import BaseUserManager

from api.auth.auth_docs import GET_DELETE_USER_ID_RESPONSE, PATCH_USER_ID_RESPONSE, PATCH_ME_RESPONSE
from api.auth.auth_manager import get_user_manager
from api.auth.auth_models import User
from api.auth.auth_schemas import UserRead, UserUpdate, UserAdminUpdate
from api.auth.base_config import current_user
from api.feedback.feedback_db import delete_feedback_by_question_author_db
from api.question.question_db import get_questions_id_db, delete_all_questions_db
from api.rating.rating_db import get_rating_user_id, delete_rating_db
from api.rating.rating_docs import SERVER_ERROR_AUTHORIZED_RESPONSE
from api.section.section_service import SectionService
from api.university.unviversity_service import UniversityService
from core.dependecies import UOWDep, CurrentUser, CurrentSuperUser, Session
from utilties.custom_exceptions import OutOfUniversityIdException, NotAllowedPatching, OutOfSectionIdException
from utilties.error_code import ErrorCode

manage_users_router = APIRouter()


async def get_user_or_404(
        user_id: int = Query(gt=0),
        user_manager: BaseUserManager = Depends(get_user_manager),
) -> User:
    try:
        parsed_id = user_manager.parse_id(user_id)
        return await user_manager.get(parsed_id)

    except (exceptions.UserNotExists, exceptions.InvalidID):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorCode.USER_NOT_EXISTS)


@manage_users_router.get(
    "/me",
    response_model=UserRead,
    name="users:current_user",
    responses=SERVER_ERROR_AUTHORIZED_RESPONSE
)
async def me(
        user: CurrentUser,
):
    return schemas.model_validate(UserRead, obj=user)


@manage_users_router.patch(
    "/me",
    response_model=UserRead,
    dependencies=[Depends(current_user)],
    name="users:patch_current_user",
    responses=PATCH_ME_RESPONSE
)
async def update_me(
        request: Request,
        user_update: UserUpdate,  # type: ignore
        uow: UOWDep,
        session: Session,
        verified_user: CurrentUser,
        user_manager: BaseUserManager = Depends(get_user_manager),
):
    try:
        # Check whether user changed university_id to valid one
        await UniversityService().get_university_by_id(uow=uow, university_id=user_update.university_id)

        # Check whether user changed section_id to valid one
        if user_update.section_id is not None:
            await SectionService().get_section_by_id(uow=uow, section_id=user_update.section_id)

        if verified_user.role_id == 1 and user_update.university_id != verified_user.university_id:
            # Prevent user from changing own university if he had taken quiz before
            get_user_rating = await get_rating_user_id(user_id=verified_user.id, session=session)

            if get_user_rating:
                raise NotAllowedPatching

        if verified_user.role_id == 2 and user_update.section_id != verified_user.section_id:
            # Prevent user from changing own section if he had added question before
            questions_by_user = await get_questions_id_db(user_id=verified_user.id, session=session)

            if questions_by_user:
                raise NotAllowedPatching

        verified_user = await user_manager.update(
            user_update, verified_user, safe=True, request=request
        )
        return schemas.model_validate(UserRead, obj=verified_user)

    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.reason)

    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
        )

    except OutOfSectionIdException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.OUT_OF_SECTION_ID)

    except OutOfUniversityIdException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.OUT_OF_UNIVERSITY_ID)

    except NotAllowedPatching:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail=ErrorCode.NOT_ALLOWED_PATCHING)

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@manage_users_router.get(
    path="/id",
    response_model=UserRead,
    name="users:user",
    responses=GET_DELETE_USER_ID_RESPONSE
)
async def get_user(
        current_superuser: CurrentSuperUser,
        user=Depends(get_user_or_404)
):
    return schemas.model_validate(UserRead, obj=user)


@manage_users_router.patch(
    "/by_admin",
    response_model=UserRead,
    name="users:patch other users by id",
    responses=PATCH_USER_ID_RESPONSE
)
async def update_user(
        user_update: UserAdminUpdate,  # type: ignore
        request: Request,
        current_superuser: CurrentSuperUser,
        uow: UOWDep,
        user=Depends(get_user_or_404),
        user_manager: BaseUserManager = Depends(get_user_manager),
):
    try:
        # Check whether user changed university_id to valid one
        await UniversityService().get_university_by_id(uow=uow, university_id=user_update.university_id)

        if user_update.section_id is not None:
            # Check whether user changed section_id to valid one
            await SectionService().get_section_by_id(uow=uow, section_id=user_update.section_id)

        user = await user_manager.update(
            user_update, user, safe=False, request=request
        )
        return schemas.model_validate(UserRead, obj=user)

    except OutOfSectionIdException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.OUT_OF_SECTION_ID)

    except OutOfUniversityIdException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorCode.OUT_OF_UNIVERSITY_ID)

    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.reason,
        )

    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
        )

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=Exception)


@manage_users_router.delete(
    path="/user",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    name="users:delete_user",
    responses=GET_DELETE_USER_ID_RESPONSE
)
async def delete_user(
        current_superuser: CurrentSuperUser,
        session: Session,
        user_for_delete=Depends(get_user_or_404),
        user_manager: BaseUserManager = Depends(get_user_manager),
):
    user_id = user_for_delete.id
    if user_for_delete.role_id == 1:
        # Delete all records in rating table for the student
        await delete_rating_db(user_id=user_id, session=session)

    else:
        # Delete all records in feedback table that question author get
        await delete_feedback_by_question_author_db(user_id=user_id, session=session)

        # Delete all records in questions table for the user
        await delete_all_questions_db(user_id=user_id, session=session)

    await user_manager.delete(user_for_delete)
    return None
