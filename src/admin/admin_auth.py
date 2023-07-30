from typing import Optional
from urllib.request import Request

from fastapi_users import exceptions
from fastapi_users.exceptions import UserNotExists
from sqladmin.authentication import AuthenticationBackend
from starlette.responses import RedirectResponse

from admin.admin_auth_service import authenticate_service
from auth.auth_manager import UserManager
from utilties.password_manager import PasswordManager


class AdminAuth(AuthenticationBackend, UserManager):

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]

        is_logged_in = await authenticate_service(email=email, password=password)

        if is_logged_in is not None:
            return False

        request.session.update({"token": "..."})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        if "token" not in request.session:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
