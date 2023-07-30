from section.section_schemas import Section
from utilties.repository import SQLAlchemyRepository


class SectionRepository(SQLAlchemyRepository):
    model = Section
