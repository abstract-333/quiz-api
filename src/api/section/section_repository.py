from api.section.section_schemas import Section
from common.repository import SQLAlchemyRepository


class SectionRepository(SQLAlchemyRepository):
    model = Section
