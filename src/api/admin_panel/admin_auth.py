from typing import Optional
from urllib.request import Request

from sqladmin.authentication import AuthenticationBackend
from starlette.responses import RedirectResponse

from api.admin_panel.admin_auth_service import authenticate_service
from api.auth.auth_manager import UserManager


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
            return RedirectResponse(request.url_for("admin_panel:login"), status_code=302)
