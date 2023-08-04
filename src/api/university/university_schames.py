from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from database import Base


class UniversitySchema(BaseModel):
    id: int
    name: str


class University(Base):
    __tablename__ = "university"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=25), nullable=False)

    def to_read_model(self) -> UniversitySchema:
        return UniversitySchema(
            id=self.id,
            name=self.name
        )
