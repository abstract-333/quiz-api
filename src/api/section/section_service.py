from api.section.section_schemas import SectionSchema
from core.unit_of_work import IUnitOfWork
from utilties.custom_exceptions import OutOfSectionIdException


class SectionService:
    @staticmethod
    async def get_sections(uow: IUnitOfWork) -> list[SectionSchema | None]:
        """Get list of all sections"""
        async with uow:
            sections = await uow.section.find_by()
            return sections

    @staticmethod
    async def get_section_by_name(uow: IUnitOfWork, name: str) -> SectionSchema | None:
        """Get section by name"""
        async with uow:
            section = await uow.section.find_one(name=name)
            return section

    @staticmethod
    async def _get_section_by_id(uow: IUnitOfWork, section_id: int) -> SectionSchema | None:
        """Get section by section_id without raising exception"""
        async with uow:
            section = await uow.section.find_one(id=section_id)

            # Raise exception if the section_id not valid
            if not section:
                raise OutOfSectionIdException

            return section

    async def get_section_by_id(self, uow: IUnitOfWork, section_id: int) -> SectionSchema | None:
        """Get section by section_id"""
        async with uow:
            section = await self._get_section_by_id(uow=uow, section_id=section_id)

            # Raise exception if the section_id not valid
            if not section:
                raise OutOfSectionIdException

            return section
