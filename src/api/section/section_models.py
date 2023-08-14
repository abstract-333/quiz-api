from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from api.section.section_schemas import SectionSchema
from database import Base


class Section(Base):
    __tablename__ = "section"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[int] = mapped_column(String(length=25), nullable=False, unique=True)

    def to_read_model(self) -> SectionSchema:
        return SectionSchema(
            id=self.id,
            name=self.name
        )
