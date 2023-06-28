from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Integer, Column, String, TIMESTAMP, ForeignKey

from auth.auth_models import user
from blacklist.blacklist_models import blocked_level
from database import Base


class BlacklistCreate(BaseModel):
    user_id: int
    blocking_level: int = 1


class BlacklistRead(BaseModel):
    user_id: int


class BlacklistUpdate(BaseModel):
    blocking_level: int
    blocked_at: datetime = datetime.utcnow()


class BlockedLevel(Base):
    __tablename__ = "blocked_level"
    id = Column(Integer, primary_key=True)
    unblocked_after = Column(Integer, nullable=True)
    description = Column(String(length=100), nullable=True)


class Blacklist(Base):
    __tablename__ = "blacklist"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(user.c.id), nullable=False)
    blocking_level = Column(Integer, ForeignKey(blocked_level.c.id), nullable=False)
    blocked_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
