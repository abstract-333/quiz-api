from typing import Optional
from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    id: int
    username: str
    email: str
    role_id: int
    phone: Optional[str]
    university_id: Optional[int]
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        orm_mode = True


class UserCreate(schemas.BaseUserCreate):
    username: str
    email: str
    password: str
    role_id: int
    phone: Optional[str]
    university_id: Optional[int]
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    email: str
    phone: str
    role_id: int
    phone: Optional[str]
    university_id: Optional[int]
    is_active: Optional[bool]
    is_superuser: Optional[bool]
    is_verified: Optional[bool]

#
# class ExtendedOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
#     def __init__(self,
#                  # email: str = Form(...), I've deleted this field
#                  password: str = Form(...),
#                  grant_type: str = Form(default=""),
#                  scope: str = Form(default=""),
#                  client_id: Optional[str] = Form(default=None),
#                  client_secret: Optional[str] = Form(default=None), ):
#         super().__init__(
#             grant_type=grant_type,
#             username="",
#             password=password,
#             scope=scope,
#             client_id=client_id,
#             client_secret=client_secret,
#         )
