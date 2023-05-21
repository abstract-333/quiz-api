from datetime import datetime

from sqlalchemy import MetaData, Table, Column, Integer, ForeignKey, TIMESTAMP

from auth.models import user
from university.models import university

metadata = MetaData()

rating = Table(
    "rating",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey(user.c.id), nullable=False),
    Column("university_id", Integer, ForeignKey(university.c.id), nullable=False),
    Column("questions_number", Integer, nullable=False),
    Column("solved", Integer, nullable=False),
    Column("added_at", TIMESTAMP, default=datetime.utcnow, nullable=False)
)
