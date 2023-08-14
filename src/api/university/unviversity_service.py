from api.university.university_schames import UniversitySchema
from core.unit_of_work import IUnitOfWork
from utilties.custom_exceptions import OutOfUniversityIdException


class UniversityService:
    @staticmethod
    async def get_universities(uow: IUnitOfWork) -> list[UniversitySchema | None]:
        """Get list of all universities"""
        async with uow:
            universities = await uow.university.find_by()
            return universities

    @staticmethod
    async def get_university_by_name(uow: IUnitOfWork, name: str) -> UniversitySchema | None:
        """Get university by name"""
        async with uow:
            university = await uow.university.find_one(name=name)
            return university

    @staticmethod
    async def _get_university_by_id(uow: IUnitOfWork, university_id: int) -> UniversitySchema | None:
        """Get university by university_id without raising exception"""
        async with uow:
            university = await uow.university.find_one(id=university_id)
            return university

    async def get_university_by_id(self, uow: IUnitOfWork, university_id: int) -> UniversitySchema | None:
        """Get university by university_id and raise exception if university_id is not valid"""
        async with uow:
            university = await self._get_university_by_id(uow=uow, university_id=university_id)

            # Check that returned object is not None
            if not university:
                raise OutOfUniversityIdException

            return university
