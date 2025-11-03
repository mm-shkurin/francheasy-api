from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from app.db.database import get_db
from app.models.users import Users
from app.services.business_request_service import BusinessRequestService
from app.services.francheasy import FrancheasyService
from app.services.store_service import StoreService
from app.services.povilions_service import PovilionsService
from app.schemas.business_request import (
    BusinessRequestCreate, 
    BusinessRequestRead, 
    BusinessRequestUpdate,
    BusinessRequestListItem
)
from app.utils.security import get_current_user

business_request_router = APIRouter()


@business_request_router.post("/", response_model=BusinessRequestRead, status_code=status.HTTP_201_CREATED)
async def create_business_request(
    request: BusinessRequestCreate,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BusinessRequestService(db)
    try:
        return await service.create_request(current_user.id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@business_request_router.get("/my", response_model=List[BusinessRequestListItem])
async def list_my_requests(
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BusinessRequestService(db)
    requests_list = await service.get_requests_by_user(current_user.id)
    
    result = []
    for r in requests_list:
        francheasy_service = FrancheasyService(db)
        francheasy = await francheasy_service.get_francheasy_by_id(str(r.francheasy_id))
        francheasy_title = francheasy.title if francheasy else None
        
        store_title = None
        if r.store_id:
            store_service = StoreService(db)
            store = await store_service.get_store_by_id(r.store_id)
            if store:
                store_title = store.title
        
        povilion_title = None
        povilion_price = None
        if r.povilion_id:
            povilions_service = PovilionsService(db)
            povilion = await povilions_service.get_povilion_by_id(r.povilion_id)
            if povilion:
                povilion_title = povilion.title
                povilion_price = povilion.price
        
        result.append(
            BusinessRequestListItem(
                request_id=r.request_id,
                user_id=r.user_id,
                francheasy_id=r.francheasy_id,
                francheasy_title=francheasy_title,
                store_id=r.store_id,
                store_title=store_title,
                povilion_id=r.povilion_id,
                povilion_title=povilion_title,
                povilion_price=povilion_price,
                status=r.status,
                created_at=r.created_at
            )
        )
    return result


@business_request_router.get("/francheasy", response_model=List[BusinessRequestListItem])
async def list_francheasy_requests(
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BusinessRequestService(db)
    requests_list = await service.get_requests_by_francheasy_owner(current_user.id)
    
    result = []
    for r in requests_list:
        francheasy_service = FrancheasyService(db)
        francheasy = await francheasy_service.get_francheasy_by_id(str(r.francheasy_id))
        francheasy_title = francheasy.title if francheasy else None
        
        store_title = None
        if r.store_id:
            store_service = StoreService(db)
            store = await store_service.get_store_by_id(r.store_id)
            if store:
                store_title = store.title
        
        povilion_title = None
        povilion_price = None
        if r.povilion_id:
            povilions_service = PovilionsService(db)
            povilion = await povilions_service.get_povilion_by_id(r.povilion_id)
            if povilion:
                povilion_title = povilion.title
                povilion_price = povilion.price
        
        result.append(
            BusinessRequestListItem(
                request_id=r.request_id,
                user_id=r.user_id,
                francheasy_id=r.francheasy_id,
                francheasy_title=francheasy_title,
                store_id=r.store_id,
                store_title=store_title,
                povilion_id=r.povilion_id,
                povilion_title=povilion_title,
                povilion_price=povilion_price,
                status=r.status,
                created_at=r.created_at
            )
        )
    return result


@business_request_router.put("/{request_id}/status", response_model=BusinessRequestRead)
async def update_request_status(
    request_id: UUID,
    status_update: BusinessRequestUpdate,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BusinessRequestService(db)
    try:
        updated = await service.update_request_status(request_id, current_user.id, status_update)
        if not updated:
            raise HTTPException(status_code=404, detail="Request not found")
        
        return BusinessRequestRead(
            request_id=updated.request_id,
            user_id=updated.user_id,
            francheasy_id=updated.francheasy_id,
            store_id=updated.store_id,
            povilion_id=updated.povilion_id,
            status=updated.status,
            created_at=updated.created_at,
            updated_at=updated.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@business_request_router.get("/{request_id}", response_model=BusinessRequestRead)
async def get_request_details(
    request_id: UUID,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BusinessRequestService(db)
    request = await service.get_request_by_id(request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return BusinessRequestRead(
        request_id=request.request_id,
        user_id=request.user_id,
        francheasy_id=request.francheasy_id,
        store_id=request.store_id,
        povilion_id=request.povilion_id,
        status=request.status,
        created_at=request.created_at,
        updated_at=request.updated_at
    )

