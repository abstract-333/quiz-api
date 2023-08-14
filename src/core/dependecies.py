from typing import Annotated

from fastapi import Depends

from api.auth.auth_models import User
from api.auth.base_config import current_user, current_superuser, unverified_user
from core.unit_of_work import UnitOfWork, IUnitOfWork

UOWDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]
CurrentUser = Annotated[User, Depends(current_user)]
CurrentSuperUser = Annotated[User, Depends(current_superuser)]
CurrentUnverifiedUser = Annotated[User, Depends(unverified_user)]
