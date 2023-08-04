from typing import Generic, TypeVar
from utilties.custom_exceptions import NothingFound

SchemaRead = TypeVar('SchemaRead')
SchemaCreate = TypeVar('SchemaCreate')
SchemaUpdate = TypeVar('SchemaUpdate')


class Service(Generic[SchemaRead, SchemaCreate, SchemaUpdate]):
    repo = None

    async def add_entity(self, entity_schema: SchemaCreate) -> SchemaRead:
        """Add entity to db"""
        entity_dict = entity_schema.model_dump()
        entity = await self.repo.add_one(entity_dict)
        return entity

    async def get_entities(self) -> list[SchemaRead | None]:
        """Get list of all entities in table"""
        entities = await self.repo.find_all()
        return entities

    async def get_entity_by_id(self, entity_id: int) -> SchemaRead | None:
        """Get entity by entity_id"""
        entity = await self.repo.find_one(id=entity_id)

        # Raise exception if this entity_id not valid
        if not entity:
            raise NothingFound

        return entity

    async def get_entity_by(self,  **kwargs) -> SchemaRead | None:
        """Get entity by entity_id"""
        entity = await self.repo.find_one(**kwargs)

        return entity

    async def update_entity(self, entity_id: int, entity_update: SchemaUpdate) -> SchemaRead | None:
        """Update entity by entity_id"""
        entity = await self.repo.find_one(id=entity_id)

        # Raise exception if this entity_id not valid
        if not entity:
            raise NothingFound

        updated_entity = await self.repo.update_one(data=entity_update, id=entity_id)
        return updated_entity
