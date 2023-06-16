from typing import Optional
from urllib.request import Request

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm
from fastapi_users.authentication import backend
from fastapi_users.authentication.strategy.db import strategy
from sqladmin.authentication import AuthenticationBackend
from starlette import status
from starlette.responses import RedirectResponse

from auth.auth_manager import get_user_manager
from auth.auth_models import User
from auth.base_config import current_user
from utilties.error_code import ErrorCode


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
