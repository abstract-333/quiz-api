from sqlalchemy import insert, select, update, delete
from common.repository import AbstractRepository
from database import async_session_maker


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def add_one(self, data: dict) -> model:
        async with async_session_maker() as session:
            stmt = insert(self.model).values(**data).returning(self.model)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one()

    async def update_one(self, data: dict, **kwargs) -> model:
        async with async_session_maker() as session:
            stmt = update(self.model).filter_by(**kwargs).values(**data).returning(self.model)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one()

    async def find_all(self) -> list:
        async with async_session_maker() as session:
            query = select(self.model)
            result = await session.execute(query)
            result = [row[0].to_read_model() for row in result.all()]
            return result

    async def find_one(self, **kwargs):
        async with async_session_maker() as session:
            query = select(self.model).filter_by(**kwargs)
            result = await session.execute(query)
            row = result.scalar()

            if row:
                return row.to_read_model()
            return None

    async def delete_one(self, **kwargs) -> None:
        async with async_session_maker() as session:
            stmt = delete(self.model).filter_by(**kwargs)
            await session.execute(stmt)
            await session.commit()
            return None
