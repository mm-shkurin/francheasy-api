from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from app.models.povilions import Povilions
from app.schemas.povilions import PovilionsCreate, PovilionsUpdate
from uuid import UUID
from typing import List, Optional


class PovilionsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_povilion(self, user_id: UUID, povilion_in: PovilionsCreate) -> Povilions:
        db_povilion = Povilions(
            user_id=user_id,
            store_id=povilion_in.store_id,
            title=povilion_in.title,
            price=povilion_in.price,
        )
        self.db.add(db_povilion)
        try:
            await self.db.commit()
            await self.db.refresh(db_povilion)
            return db_povilion
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError(f"Ошибка при создании павильона: {e}")

    async def get_povilion_by_id(self, povilion_id: UUID) -> Optional[Povilions]:
        result = await self.db.execute(select(Povilions).where(Povilions.povilion_id == povilion_id))
        return result.scalar_one_or_none()

    async def get_povilions_by_store(self, store_id: UUID) -> List[Povilions]:
        result = await self.db.execute(select(Povilions).where(Povilions.store_id == store_id))
        return list(result.scalars().all())

    async def get_povilions_by_user(self, user_id: UUID) -> List[Povilions]:
        result = await self.db.execute(select(Povilions).where(Povilions.user_id == user_id))
        return list(result.scalars().all())

    async def update_povilion(self, povilion_id: UUID, povilion_in: PovilionsUpdate) -> Optional[Povilions]:
        values = povilion_in.dict(exclude_unset=True)
        if not values:
            return await self.get_povilion_by_id(povilion_id)

        await self.db.execute(
            update(Povilions)
            .where(Povilions.povilion_id == povilion_id)
            .values(**values)
        )
        await self.db.commit()
        return await self.get_povilion_by_id(povilion_id)

    async def delete_povilion(self, povilion_id: UUID) -> bool:
        result = await self.db.execute(delete(Povilions).where(Povilions.povilion_id == povilion_id))
        await self.db.commit()
        return result.rowcount > 0

