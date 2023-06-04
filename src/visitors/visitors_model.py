from datetime import datetime

from sqlalchemy import MetaData, Table, Column, Integer, TIMESTAMP, String


metadata = MetaData()

visitors = Table(
    "visitors",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("country", String(length=20), nullable=False),
    Column("count", Integer, nullable=False),
    Column("added_at", TIMESTAMP, default=datetime.utcnow, nullable=False)
)
