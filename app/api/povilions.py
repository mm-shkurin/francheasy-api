from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from app.db.database import get_db
from app.models.users import Users
from app.services.povilions_service import PovilionsService
from app.schemas.povilions import PovilionsCreate, PovilionsRead, PovilionsUpdate, PovilionsListItem
from app.utils.security import get_current_user

povilions_router = APIRouter()


@povilions_router.post("/", response_model=PovilionsRead, status_code=status.HTTP_201_CREATED)
async def create_povilion(
    povilion: PovilionsCreate,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = PovilionsService(db)
    
    # Проверяем, что магазин существует и принадлежит пользователю
    from app.services.store_service import StoreService
    store_service = StoreService(db)
    store = await store_service.get_store_by_id(povilion.store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    return await service.create_povilion(user_id=current_user.id, povilion_in=povilion)


@povilions_router.get("/store/{store_id}", response_model=List[PovilionsListItem])
async def list_povilions_by_store(
    store_id: UUID,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = PovilionsService(db)
    povilions = await service.get_povilions_by_store(store_id)
    
    result = []
    for p in povilions:
        result.append(
            PovilionsListItem(
                povilion_id=p.povilion_id,
                store_id=p.store_id,
                title=p.title,
                price=p.price
            )
        )
    return result

@povilions_router.put("/{povilion_id}", response_model=PovilionsRead)
async def update_povilion(
    povilion_id: UUID,
    povilion: PovilionsUpdate,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = PovilionsService(db)
    existing = await service.get_povilion_by_id(povilion_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Povilion not found")
    
    if existing.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this povilion")

    updated = await service.update_povilion(povilion_id, povilion)
    return PovilionsRead(
        povilion_id=updated.povilion_id,
        user_id=updated.user_id,
        store_id=updated.store_id,
        title=updated.title,
        price=updated.price,
        created_at=updated.created_at,
        updated_at=updated.updated_at
    )


@povilions_router.delete("/{povilion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_povilion(
    povilion_id: UUID,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = PovilionsService(db)
    existing = await service.get_povilion_by_id(povilion_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Povilion not found")
    
    if existing.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this povilion")

    success = await service.delete_povilion(povilion_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete povilion")

