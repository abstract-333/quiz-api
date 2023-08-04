from common.repository import AbstractRepository
from utilties.custom_exceptions import OutOfSectionIdException
from api.section.section_schemas import SectionSchema


class SectionService:
    def __init__(self, section_repo: AbstractRepository):
        self.section_repo: AbstractRepository = section_repo()

    async def _add_section(self, section_schema: SectionSchema) -> SectionSchema:
        section_dict = section_schema.model_dump()
        section_id = await self.section_repo.add_one(section_dict)
        return section_id

    async def get_sections(self) -> list[SectionSchema | None]:
        """Get list of all sections"""
        sections = await self.section_repo.find_all()
        return sections

    async def get_section_by_name(self, name: str) -> SectionSchema | None:
        """Get section by name"""
        section = await self.section_repo.find_one(name=name)
        return section

    async def get_section_by_id(self, section_id: int) -> SectionSchema | None:
        """Get section by section_id"""
        section = await self.section_repo.find_one(id=section_id)

        # Raise exception if the section_id not valid
        if not section:
            raise OutOfSectionIdException

        return section
