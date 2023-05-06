from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, MetaData, JSON

metadata = MetaData()

quiz = Table(
    "quiz",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("resolve_time", Integer, nullable=False),
    Column("question", String(length=200), nullable=False),
    Column("choices", JSON, nullable=False),
    Column("answer", String(length=25), nullable=False),
    Column("added_by", String(length=25), nullable=False),
    Column("added_at", TIMESTAMP, default=datetime.utcnow),
    Column("type", String(length=25), nullable=False)
)