from api.section.section_models import Section
from core.repository import SQLAlchemyRepository


class SectionRepository(SQLAlchemyRepository):
    main_model = Section
