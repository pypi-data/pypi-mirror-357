from typing import Generic, TypeVar, Type, Any
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import Base
from sqlalchemy.exc import SQLAlchemyError





ModelType = TypeVar("ModelType", bound=Base) #type: ignore 
SchemaType = TypeVar("SchemaType", bound=BaseModel)

class BasicCrud(Generic[ModelType, SchemaType]):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, model: Type[ModelType], obj_items: SchemaType):
        try:
            db_obj = model(**obj_items.model_dump())
            self.db.add(db_obj)
            await self.db.commit()
            await self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e

    async def get_by_id(self, model: Type[ModelType], item_id: int):
        try:
            stmt = select(model).where(model.id == item_id)
            result = await self.db.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e

    async def get_all(self, model: Type[ModelType], limit: int = 100, offset: int = 0):
        try:
            stmt = select(model).offset(offset).limit(limit)
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e

    async def get_by_field(
        self, model: Type[ModelType], field_name: str, field_value: Any
    ):
        try:
            if not hasattr(model, field_name):
                raise AttributeError(
                    f"Field '{field_name}' does not exist on {model.__name__}"
                )
            stmt = select(model).where(getattr(model, field_name) == field_value)
            result = await self.db.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e

    async def update(self, model: Type[ModelType], item_id: int, obj_items: SchemaType):
        try:
            db_obj = await self.get_by_id(item_id)
            if not db_obj:
                return None
            for key, value in obj_items.model_dump(exclude_unset=True).items():
                setattr(db_obj, key, value)
            await self.db.commit()
            return db_obj
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e

    async def delete(self, model: Type[ModelType], item_id: int):
        try:
            result = await self.get_by_id(item_id)
            if result:
                await self.db.delete(result)
                await self.db.commit()
            return result
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e