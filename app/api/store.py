from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from app.db.database import get_db
from app.models.users import Users
from app.services.store_service import StoreService
from app.schemas.store import StoreCreate, StoreRead, StoreUpdate,StoreListItem
from app.utils.security import get_current_user

store_router = APIRouter()


@store_router.post("/", response_model=StoreRead, status_code=status.HTTP_201_CREATED)
async def create_store(
    store: StoreCreate,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = StoreService(db)
    return await service.create_store(user_id=current_user.id, store_in=store)

@store_router.get("/list", response_model=List[StoreListItem])
async def list_stores(
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = StoreService(db)
    stores = await service.get_all_stores()
    
    result = []
    for s in stores:
        result.append(
            StoreListItem(
                store_id=s.store_id,
                title=s.title,
                adress=s.adress,
                cross_country_ability=s.cross_country_ability,
                latitude=s.latitude,
                longitude=s.longitude
            )
        )
    return result    

@store_router.get("/{store_id}", response_model=StoreRead)
async def get_store(
    store_id: UUID,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = StoreService(db)
    store = await service.get_store_by_id(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    return StoreRead(
        store_id=store.store_id,
        user_id=store.user_id,
        title=store.title,
        adress = store.adress,
        cross_country_ability=store.cross_country_ability,
        latitude=store.latitude,
        longitude=store.longitude,
        created_at=store.created_at,
        updated_at=store.updated_at
    )


@store_router.put("/{store_id}", response_model=StoreRead)
async def update_store(
    store_id: UUID,
    store: StoreUpdate,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = StoreService(db)
    existing = await service.get_store_by_id(store_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Store not found")
    
    if existing.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this store")

    updated = await service.update_store(store_id, store)
    return updated


@store_router.delete("/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_store(
    store_id: UUID,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = StoreService(db)
    existing = await service.get_store_by_id(store_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Store not found")
    if existing.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this store")

    success = await service.delete_store(store_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete store") 

