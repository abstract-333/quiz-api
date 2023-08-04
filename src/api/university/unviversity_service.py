from api.university.university_repository import UniversityRepository
from api.university.university_schames import UniversitySchema
from utilties.custom_exceptions import OutOfUniversityIdException, NothingFound
from common.repository import AbstractRepository
from common.service import Service


class UniversityService(Service[UniversitySchema, UniversitySchema, UniversitySchema]):
    repo: AbstractRepository = UniversityRepository()

    async def get_universities(self) -> list[UniversitySchema | None]:
        """Get list of all universities"""
        universities = await self.get_entities()
        return universities

    async def get_university_by_name(self, name: str) -> UniversitySchema | None:
        """Get university by name"""
        university = await self.get_entity_by(name=name)
        return university

    async def get_university_by_id(self, university_id: int) -> UniversitySchema | None:
        """Get university by university_id"""
        try:
            university = await self.get_entity_by_id(entity_id=university_id)

        # Raise exception if the university_id not valid
        except NothingFound:
            raise OutOfUniversityIdException

        return university
