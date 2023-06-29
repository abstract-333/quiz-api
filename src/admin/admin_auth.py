from typing import Optional
from urllib.request import Request

from fastapi import Depends
from fastapi.security import HTTPBearer
from fastapi_users import exceptions
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from auth.auth_manager import get_user_manager, UserManager
from auth.auth_models import user


class AdminAuth(AuthenticationBackend, UserManager):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        # try:
        #     user_new = await self.user_db.get_by_email(username)
        #     if user_new is None:
        #         self.password_helper.hash(password)
        #         raise exceptions.UserNotExists()
        #
        # except exceptions.UserNotExists:
        #     # Run the hasher to mitigate timing attack
        #     # Inspired from Django: https://code.djangoproject.com/ticket/20760
        #     return None
        # verified, updated_password_hash = self.password_helper.verify_and_update(
        #     password, user_new.hashed_password
        # )
        # if not verified:
        #     return None
        # # Update password hash to a more robust one if needed
        # if updated_password_hash is not None:
        #     await self.user_db.update(user_new, {"hashed_password": updated_password_hash})

        # return user_new

        # Validate username/password credentials
        # And update session
        request.session.update({"token": "..."})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        if "token" not in request.session:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
