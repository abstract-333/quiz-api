from sqlalchemy import Column, Integer, String
from database import Base


class University(Base):
    __tablename__ = "university"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=25), nullable=False)
