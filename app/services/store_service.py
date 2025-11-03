from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from app.models.store import Store
from app.schemas.store import StoreCreate, StoreUpdate
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from sqlalchemy import func

class StoreService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_store(self, user_id: UUID, store_in: StoreCreate) -> Store:
        db_store = Store(
            user_id=user_id,
            title=store_in.title,
            adress=store_in.adress,
            cross_country_ability=store_in.cross_country_ability,
            latitude=store_in.latitude,
            longitude=store_in.longitude,
        )
        self.db.add(db_store)
        try:
            await self.db.commit()
            await self.db.refresh(db_store)
            return db_store
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError(f"Ошибка при создании магазина: {e}")

    async def get_store_by_id(self, store_id: UUID) -> Optional[Store]:
        result = await self.db.execute(select(Store).where(Store.store_id == store_id))
        return result.scalar_one_or_none()

    async def get_stores_by_user(self, user_id: UUID) -> List[Store]:
        result = await self.db.execute(select(Store).where(Store.user_id == user_id))
        return list(result.scalars().all())

    async def update_store(self, store_id: UUID, store_in: StoreUpdate) -> Optional[Store]:
        values = store_in.dict(exclude_unset=True)
        if not values:
            return await self.get_store_by_id(store_id)


        await self.db.execute(
            update(Store)
            .where(Store.store_id == store_id)
            .values(**values)
        )
        await self.db.commit()
        return await self.get_store_by_id(store_id)

    async def delete_store(self, store_id: UUID) -> bool:
        result = await self.db.execute(delete(Store).where(Store.store_id == store_id))
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_all_stores(self) -> List[Store]:
        result = await self.db.execute(select(Store))
        return list(result.scalars().all())