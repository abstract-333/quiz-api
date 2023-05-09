from sqlalchemy import Integer, String, Column

from database import Base


class Section(Base):
    __tablename__ = "section"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=25), nullable=False, unique=True)