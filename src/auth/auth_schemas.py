from typing import Optional
from fastapi_users import schemas
from pydantic import EmailStr
from sqlalchemy import Column, String, Integer, JSON

from database import Base


class UserRead(schemas.BaseUser[int]):
    id: int
    username: str
    email: str
    role_id: int
    phone: Optional[str] = None
    university_id: int
    section_id: Optional[int] = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserCreate(schemas.BaseUserCreate):
    username: str
    email: str
    password: str
    role_id: int
    phone: Optional[str] = None
    university_id: int
    section_id: Optional[int] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    university_id: Optional[int] = None
    section_id: Optional[int] = None


class UserAdminUpdate(schemas.BaseUserUpdate):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    role_id: Optional[int] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    university_id: Optional[int] = None
    section_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None


class Role(Base):
    __tablename__ = "Role"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=25), nullable=False)
    permissions = Column(JSON)
