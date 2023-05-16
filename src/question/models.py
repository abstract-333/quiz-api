from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, MetaData, JSON, ForeignKey

from auth.models import user
from section.models import section

metadata = MetaData()


question = Table(
    "question",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("resolve_time", Integer, nullable=False),
    Column("question_title", String(length=200, collation="utf8mb4_general_ci"), nullable=False),
    Column("choices", JSON, nullable=False),
    Column("answer", String(length=25), nullable=False),
    Column("added_by", ForeignKey(user.c.id), nullable=False),
    Column("added_at", TIMESTAMP, default=datetime.utcnow),
    Column("section_id", Integer, ForeignKey(section.c.id), nullable=False)
)