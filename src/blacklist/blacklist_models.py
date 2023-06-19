from datetime import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey

from auth.auth_models import user

metadata = MetaData()
blocked_level = Table(
    "blocked_level",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("unblocked_after", Integer, nullable=True),
    Column("description", String(length=100), nullable=True)
)
blacklist = Table(
    "blacklist",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey(user.c.id), nullable=False),
    Column("blocking_level", Integer, ForeignKey(blocked_level.c.id), nullable=False),
    Column("blocked_at", TIMESTAMP, default=datetime.utcnow, nullable=False),
)
