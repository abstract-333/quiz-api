from typing import Optional, Union
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models, schemas, jwt
from fastapi_users.jwt import decode_jwt
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse
from auth.models import User
from auth.schemas import UserCreate
from config import SECRET_KEY
from database import get_async_session, async_session_maker
from utils.password_manager import PasswordManager
from utils.constants import Constants
from utils.email import send_email


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    _SECRET = SECRET_KEY
    reset_password_token_secret = _SECRET
    verification_token_secret = _SECRET

    # async def authenticate(
    #         self, credentials: ExtendedOAuth2PasswordRequestForm,
    #         session: AsyncSession = Depends(get_async_session)
    # ) -> Optional[bool]:
    #     """
    #     Authenticate and return a user following an email and a password.
    #
    #     Will automatically upgrade password hash if necessary.
    #
    #     :param session:
    #     :param credentials: The user credentials.
    #     """
    #     query = select(user).where(user.c.student_id == credentials.student_id)
    #     try:
    #         result_proxy = await session.execute(query)
    #         user_new = result_proxy.first()
    #         if user_new is None:
    #             self.password_helper.hash(credentials.password)
    #             raise exceptions.UserNotExists()
    #
    #     except exceptions.UserNotExists:
    #         # Run the hasher to mitigate timing attack
    #         # Inspired from Django: https://code.djangoproject.com/ticket/20760
    #         return None
    #     verified, updated_password_hash = self.password_helper.verify_and_update(
    #         credentials.password, user_new.hashed_password
    #     )
    #     if not verified:
    #         return None
    #     # Update password hash to a more robust one if needed
    #     if updated_password_hash is not None:
    #         await self.user_db.update(user_new, {"hashed_password": updated_password_hash})
    #
    #     return user_new

    async def validate_password(
            self,
            password: str,
            user: Union[UserCreate, User],
    ) -> None:
        PasswordManager.validate_password(password, user)

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        send_email.delay(user.username, Constants.RESET_PASSWORD, user.email, token)
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        send_email.delay(user.username, Constants.EMAIL_CONFIRM, user.email, token)
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def verify(self, token: str, request: Optional[Request] = None) -> models.UP:
        try:
            data = decode_jwt(
                token,
                self.verification_token_secret,
                [self.verification_token_audience],
            )
        except jwt.PyJWTError:
            raise exceptions.InvalidVerifyToken()

        try:
            user_id = data["sub"]
            email = data["email"]
        except KeyError:
            raise exceptions.InvalidVerifyToken()

        try:
            user = await self.get_by_email(email)
        except exceptions.UserNotExists:
            raise exceptions.InvalidVerifyToken()

        try:
            parsed_id = self.parse_id(user_id)
        except exceptions.InvalidID:
            raise exceptions.InvalidVerifyToken()

        if parsed_id != user.id:
            raise exceptions.InvalidVerifyToken()

        if user.is_verified:
            raise exceptions.UserAlreadyVerified()

        verified_user = await self._update(user, {"is_verified": True})

        await self.on_after_verify(verified_user, request)

        html_content = f'''<div dir="rtl"><center>
                                <h1>تم توثيق البريد الالكتروني بنجاح</h1>
                                <h2>شكراً لك {user.username}</h2>
                                </center>
                                </div>'''
        return HTMLResponse(status_code=200, content=html_content)

    async def on_after_register(
            self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        # await self.request_verify(user, request)
        return None

    async def create(
            self,
            user_create: schemas.UC,
            safe: bool = False,
            request: Optional[Request] = None,
            # session: AsyncSession = Depends(get_async_session)
    ) -> models.UP:

        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)

        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        if user_create.university_id not in range(1, 8):
            user_dict["university_id"] = None
        if user_create.role_id in (1, 2):
            user_dict["role_id"] = user_create.role_id
        else:
            user_dict["role_id"] = 1

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)
        delattr(created_user, "hashed_password")

        return created_user


async def get_user_db(session: AsyncSession = Depends(get_async_session)) -> SQLAlchemyUserDatabase:
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db=Depends(get_user_db)) -> UserManager:
    yield UserManager(user_db, PasswordManager.password_helper)
