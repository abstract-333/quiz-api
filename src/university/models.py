from sqlalchemy import MetaData, Table, Column, Integer, String

from database import Base

metadata = MetaData()

university = Table(
    "university",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(length=25), nullable=False)
)


class University(Base):
    __tablename__ = "university"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=25), nullable=False)
