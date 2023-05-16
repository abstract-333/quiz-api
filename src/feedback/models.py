from datetime import datetime

import mysql
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, SmallInteger
from sqlalchemy.dialects.mysql import SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from auth.models import user
from database import Base
from question.models import question

metadata = MetaData()

feedback = Table(
    "feedback",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("rating", SMALLINT(unsigned=True), nullable=False),
    Column("feedback_title", String(length=1024, collation="utf8mb4_general_ci"), nullable=False),
    Column("added_at", TIMESTAMP, default=datetime.utcnow),
    Column("user_id", Integer, ForeignKey(user.c.id), nullable=False),
    Column("question_id", Integer, ForeignKey(question.c.id), nullable=False)
)
