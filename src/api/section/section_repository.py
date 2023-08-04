from api.section.section_schemas import Section
from common.sqlalchemy_repository import SQLAlchemyRepository


class SectionRepository(SQLAlchemyRepository):
    model = Section
