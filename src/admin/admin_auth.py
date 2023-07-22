from typing import Optional
from urllib.request import Request

from fastapi_users import exceptions
from sqladmin.authentication import AuthenticationBackend
from starlette.responses import RedirectResponse

from admin.admin_auth_db import get_user_db
from auth.auth_manager import UserManager
from utilties.password_manager import PasswordManager

class AdminAuth(AuthenticationBackend, UserManager):

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]
        password_helper = PasswordManager().password_helper

        # try:
        #     user_taken = await get_user_db(email)
        #     print(user_taken)
        #
        #     if not user_taken:
        #         password_helper.hash(password)
        #         raise exceptions.UserNotExists()
        #
        # except exceptions.UserNotExists:
        #     # Run the hasher to mitigate timing attack
        #     # Inspired from Django: https://code.djangoproject.com/ticket/20760
        #     return False
        #
        # verified, updated_password_hash = password_helper.verify_and_update(
        #     password, user_taken["hashed_password"]
        # )
        # if not verified:
        #     return False
        #
        # if user_taken["role_id"] != 3:
        #     return False

        request.session.update({"token": "..."})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        if "token" not in request.session:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
