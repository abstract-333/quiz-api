from api.section.section_repository import SectionRepository
from api.section.section_service import SectionService


def section_service_dependency():
    return SectionService(SectionRepository)