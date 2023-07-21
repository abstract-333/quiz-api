from typing import Optional
from fastapi_users import schemas
from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, JSON

from database import Base


class UserRead(schemas.BaseUser[int]):
    id: int
    username: str
    email: str
    role_id: int
    phone: Optional[str]
    university_id: int
    section_id: Optional[int]
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
    university_id: int
    section_id: Optional[int]
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(BaseModel):
    username: str
    email: str
    password: Optional[str]
    phone: Optional[str]
    university_id: int
    section_id: Optional[int]


class UserAdminUpdate(schemas.BaseUserUpdate):
    email: str
    username: str
    phone: str
    role_id: int
    password: Optional[str]
    phone: Optional[str]
    university_id: int
    section_id: Optional[int]
    is_active: Optional[bool]
    is_superuser: Optional[bool]
    is_verified: Optional[bool]


class Role(Base):
    __tablename__ = "Role"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=25), nullable=False)
    permissions = Column(JSON)

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
