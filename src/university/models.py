from sqlalchemy import MetaData, Table, Column, Integer, String

metadata = MetaData()

university = Table(
    "university",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(25), nullable=False)
)
