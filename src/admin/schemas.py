from typing import Optional
from urllib.request import Request

from fastapi import Depends
from fastapi.security import HTTPBearer
from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.responses import RedirectResponse

from auth.base_config import current_user
from auth.models import User
from university.models import University


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    column_list = [User.id, User.username, User.email, ]
    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True


class UniversityAdmin(ModelView, model=University):
    name = "University"
    name_plural = "Universities"
    column_list = [University.id, University.name]

    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request, dependencies=[Depends(HTTPBearer())], verified_user: User = Depends(current_user)) -> bool:
        request.session.update({"token": "..."})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        if not "token" in request.session:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
