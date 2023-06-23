from typing import Optional
from urllib.request import Request

from fastapi import Depends
from sqladmin.authentication import AuthenticationBackend
from starlette.responses import RedirectResponse

from auth.auth_manager import get_user_manager


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request, user_manager=Depends(get_user_manager)) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

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
