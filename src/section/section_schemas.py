from pydantic import BaseModel
from sqlalchemy import Integer, String, Column

from database import Base


class SectionSchema(BaseModel):
    id: int
    name: str


class Section(Base):
    __tablename__ = "section"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=25), nullable=False, unique=True)

    def to_read_model(self) -> SectionSchema:
        return SectionSchema(
            id=self.id,
            name=self.name
        )
