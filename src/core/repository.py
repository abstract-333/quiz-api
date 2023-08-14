from abc import abstractmethod
from typing import Protocol

from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(Protocol):

    @abstractmethod
    async def add_one(self, data: dict):
        ...

    @abstractmethod
    async def edit_one(self, data: dict, **kwargs):
        ...

    @abstractmethod
    async def find_by(self, offset: int = None, limit: int = None, **kwargs):
        ...

    @abstractmethod
    async def find_one(self, *args, **kwargs):
        ...

    @abstractmethod
    async def join(self, **kwargs):
        ...

    @abstractmethod
    async def delete_one(self, **kwargs):
        ...


class SQLAlchemyRepository(AbstractRepository):
    main_model = None
    second_model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict) -> main_model:
        stmt = insert(self.main_model).values(**data).returning(self.main_model)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def edit_one(self, data: dict, **kwargs) -> main_model:
        data = self.main_model.dict(exclude_unset=True)
        stmt = update(self.main_model).filter_by(**kwargs).values(**data).returning(self.main_model)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def find_by(self, offset: int = None, limit: int = None, **kwargs) -> list:
        query = select(self.main_model).filter_by(**kwargs).offset(offset).limit(limit)
        result = await self.session.execute(query)
        result = [row[0].to_read_model() for row in result.all()]
        return result

    async def find_one(self, *args, **kwargs):
        query = select(self.main_model).filter_by(**kwargs).order_by(*args)
        result = await self.session.execute(query)
        result = result.one_or_none()

        # Return None if result is equal to it
        if not result:
            return None

        # Return first row of the result
        result = result[0].to_read_model()
        return result

    async def join(self, **kwargs):
        joined_tables_query = select(self.main_model, self.second_model).join(self.second_model).filter_by(**kwargs)
        result = await self.session.execute(joined_tables_query)
        result = [row[0].to_read_model() for row in result.all()]
        return result

    async def delete_one(self, **kwargs) -> None:
        stmt = delete(self.main_model).filter_by(**kwargs)
        await self.session.execute(stmt)
        return None
