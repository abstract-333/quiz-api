from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, MetaData, JSON, ForeignKey

metadata = MetaData()


section = Table(
    "section",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(length=25), nullable=False, unique=True)
)
