from datetime import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey

from auth.auth_models import user

metadata = MetaData()

warning = Table(
    "warning",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey(user.c.id), nullable=False),
    Column("warning_level", Integer, nullable=False),
)
