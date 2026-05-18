from typing import Generic, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base

# Deux variables de type (Generics) pour l'indépendance du modèle
ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> ModelType | None:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def delete(self, db: AsyncSession, id: int) -> ModelType | None:
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj