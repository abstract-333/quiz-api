from abc import ABC
from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession

from api.blacklist.blacklist_models import Blacklist, BlockedLevel
from api.section.section_repository import SectionRepository
from api.university.university_repository import UniversityRepository
from core.repository import SQLAlchemyRepository
from database import async_session_maker


class BlacklistRepository(SQLAlchemyRepository):
    main_model = Blacklist
    second_model = BlockedLevel


class IUnitOfWork(ABC):
    section: Type[SectionRepository]
    university: Type[UniversityRepository]
    # blocked_level : Type[BlockedLevel]
    blacklist: Type[Blacklist]

    def __init__(self):
        raise NotImplementedError

    async def __aenter__(self):
        raise NotImplementedError

    async def __aexit__(self, *args):
        raise NotImplementedError

    async def commit(self):
        raise NotImplementedError

    async def rollback(self):
        raise NotImplementedError


class UnitOfWork(IUnitOfWork):

    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()

        self.section = SectionRepository(self.session)
        self.university = UniversityRepository(self.session)
        self.blacklist = BlacklistRepository(self.session)

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
