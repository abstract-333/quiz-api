from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, MetaData, JSON, ForeignKey

from section.models import section

metadata = MetaData()

basics_questions = Table(
    "basics_questions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("resolve_time", Integer, nullable=False),
    Column("question_title", String(length=200), nullable=False),
    Column("choices", JSON, nullable=False),
    Column("answer", String(length=25), nullable=False),
    Column("added_by", String(length=25), nullable=False),
    Column("added_at", TIMESTAMP, default=datetime.utcnow),
    Column("section_id", Integer, ForeignKey(section.c.id), nullable=False, default=1)
)

software_questions = Table(
    "software_questions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("resolve_time", Integer, nullable=False),
    Column("question_title", String(length=200), nullable=False),
    Column("choices", JSON, nullable=False),
    Column("answer", String(length=25), nullable=False),
    Column("added_by", String(length=25), nullable=False),
    Column("added_at", TIMESTAMP, default=datetime.utcnow),
    Column("section_id", Integer, ForeignKey(section.c.id), nullable=False, default=2)
)
ai_questions = Table(
    "ai_questions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("resolve_time", Integer, nullable=False),
    Column("question_title", String(length=200), nullable=False),
    Column("choices", JSON, nullable=False),
    Column("answer", String(length=25), nullable=False),
    Column("added_by", String(length=25), nullable=False),
    Column("added_at", TIMESTAMP, default=datetime.utcnow),
    Column("section_id", Integer, ForeignKey(section.c.id), nullable=False, default=3)
)
network_questions = Table(
    "network_questions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("resolve_time", Integer, nullable=False),
    Column("question_title", String(length=200), nullable=False),
    Column("choices", JSON, nullable=False),
    Column("answer", String(length=25), nullable=False),
    Column("added_by", String(length=25), nullable=False),
    Column("added_at", TIMESTAMP, default=datetime.utcnow),
    Column("section_id", Integer, ForeignKey(section.c.id), nullable=False, default=4)
)

QUESTIONS_SECTIONS = [basics_questions, software_questions, ai_questions, network_questions]
