from datetime import datetime

from pydantic import BaseModel


class BlacklistCreate(BaseModel):
    id: int
    user_id: int
    blocking_level: int = 1


class BlacklistRead(BaseModel):
    id: int
    user_id: int
    blocking_level: int
    blocked_at: datetime


class BlacklistUpdate(BaseModel):
    blocking_level: int
    blocked_at: datetime = datetime.utcnow()


class BlockedLevelSchema(BaseModel):
    id: int
    unblocked_after: int
