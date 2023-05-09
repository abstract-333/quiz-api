from typing import Optional
from urllib.request import Request

from fastapi import Depends
from fastapi.security import HTTPBearer
from sqladmin.authentication import AuthenticationBackend
from starlette.responses import RedirectResponse

from auth.base_config import current_user
from auth.models import User



class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request, dependencies=[Depends(HTTPBearer())],
                    verified_user: User = Depends(current_user)) -> bool:
        request.session.update({"token": "..."})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        if "token" not in request.session:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
