from section.section_repository import SectionRepository
from section.section_service import SectionService


def section_service_dependency():
    return SectionService(SectionRepository)