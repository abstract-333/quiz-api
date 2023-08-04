
from pydantic import BaseModel
from sqlalchemy import Integer, Column, ForeignKey

from api.auth.auth_models import user
from database import Base


class WarningCreate(BaseModel):
    user_id: int
    warning_level: int = 1


class WarningRead(BaseModel):
    user_id: int


class WarningUpdate(BaseModel):
    user_id: int
    warning_level: int


class WarningClass(Base):
    __tablename__ = "warning"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(user.c.id), nullable=False)
    warning_level = Column(Integer, nullable=False)
