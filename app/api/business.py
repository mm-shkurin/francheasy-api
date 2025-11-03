from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from app.db.database import get_db
from app.models.users import Users
from app.services.business_service import BusinessService
from app.services.s3_service import s3_service
from app.schemas.business import (
    BusinessRead, 
    BusinessListItem,
    TransactionCreate,
    TransactionRead
)
from app.utils.security import get_current_user
from datetime import datetime

business_router = APIRouter()


@business_router.get("/my", response_model=List[BusinessListItem])
async def list_my_businesses(
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BusinessService(db)
    businesses_list = await service.get_businesses_by_user(current_user.id)
    
    result = []
    for b in businesses_list:
        totals = service.calculate_totals(b)
        
        francheasy_title = None
        store_address = None
        povilion_title = None
        
        from app.services.francheasy import FrancheasyService
        from app.services.store_service import StoreService
        from app.services.povilions_service import PovilionsService
        
        francheasy_service = FrancheasyService(db)
        francheasy = await francheasy_service.get_francheasy_by_id(str(b.francheasy_id))
        if francheasy:
            francheasy_title = francheasy.title
        
        if b.store_id:
            store_service = StoreService(db)
            store = await store_service.get_store_by_id(b.store_id)
            if store:
                store_address = store.adress
        
        if b.povilion_id:
            povilions_service = PovilionsService(db)
            povilion = await povilions_service.get_povilion_by_id(b.povilion_id)
            if povilion:
                povilion_title = povilion.title
        
        result.append(
            {
                "business_id": b.business_id,
                "francheasy_id": b.francheasy_id,
                "francheasy_title": francheasy_title,
                "store_id": b.store_id,
                "store_address": store_address,
                "povilion_id": b.povilion_id,
                "povilion_title": povilion_title,
                "total_income": totals["total_income"],
                "total_expense": totals["total_expense"],
                "balance": totals["balance"],
                "profit_percentage": totals["profit_percentage"]
            }
        )
    return result


@business_router.get("/{business_id}", response_model=dict)
async def get_business_details(
    business_id: UUID,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BusinessService(db)
    business = await service.get_business_by_id(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    if business.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this business")
    
    totals = service.calculate_totals(business)
    
    from app.services.francheasy import FrancheasyService
    from app.services.store_service import StoreService
    from app.services.povilions_service import PovilionsService
    
    francheasy_service = FrancheasyService(db)
    francheasy = await francheasy_service.get_francheasy_by_id(str(business.francheasy_id))
    francheasy_title = francheasy.title if francheasy else None
    
    francheasy_photo_url = None
    if francheasy and francheasy.s3_photo_francheasy_keys:
        keys = francheasy.s3_photo_francheasy_keys or []
        if keys:
            francheasy_photo_url = await s3_service.generate_presigned_url(keys[0])
    
    store_address = None
    if business.store_id:
        store_service = StoreService(db)
        store = await store_service.get_store_by_id(business.store_id)
        if store:
            store_address = store.adress
    
    povilion_title = None
    if business.povilion_id:
        povilions_service = PovilionsService(db)
        povilion = await povilions_service.get_povilion_by_id(business.povilion_id)
        if povilion:
            povilion_title = povilion.title
    
    transactions = []
    for t in (business.transactions if business.transactions else []):
        transactions.append({
            "type": t.get("type"),
            "amount": t.get("amount"),
            "description": t.get("description"),
            "date": t.get("date")
        })
    
    return {
        "business_id": business.business_id,
        "francheasy_title": francheasy_title,
        "francheasy_photo_url": francheasy_photo_url,
        "store_address": store_address,
        "povilion_title": povilion_title,
        "total_expense": totals["total_expense"],
        "total_income": totals["total_income"],
        "profit_percentage": totals["profit_percentage"],
        "transactions": transactions,
        "created_at": business.created_at,
        "updated_at": business.updated_at
    }


@business_router.post("/{business_id}/transaction")
async def add_transaction(
    business_id: UUID,
    transaction: TransactionCreate,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BusinessService(db)
    business = await service.get_business_by_id(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    if business.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add transactions")
    
    updated_business = await service.add_transaction(business_id, transaction)
    if not updated_business:
        raise HTTPException(status_code=500, detail="Failed to add transaction")
    
    totals = service.calculate_totals(updated_business)
    
    return {
        "business_id": updated_business.business_id,
        "transaction_added": True,
        "total_income": totals["total_income"],
        "total_expense": totals["total_expense"],
        "balance": totals["balance"],
        "profit_percentage": totals["profit_percentage"]
    }

