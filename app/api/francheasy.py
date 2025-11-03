from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db.database import get_db
from app.models.users import Users
from app.services.francheasy import FrancheasyService
from app.schemas.francheasy import FrancheasyResponse, FrancheasyUpdate, FrancheasyUpdateResponse
from app.utils.security import get_current_user
from app.services.s3_service import s3_service

francheasy_router = APIRouter()

@francheasy_router.post("/", response_model=FrancheasyResponse, status_code=status.HTTP_201_CREATED)
async def create_francheasy(
    phone_number: str = Form(...,),
    ebitda: float = Form(...,),
    start_capital: float = Form(...,),
    open_store: float = Form(...,),
    title: Optional[str] = Form(None,),
    files: Optional[List[UploadFile]] = File(None,),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = FrancheasyService(db)
    
    try:
        from app.schemas.francheasy import FrancheasyCreate
        francheasy_create = FrancheasyCreate(
            phone_number=phone_number,
            ebitda=ebitda,
            start_capital=start_capital,
            open_store=open_store,
            title=title,
            photos_b64=[]
        )
        
        francheasy = await service.create_francheasy(str(current_user.id), francheasy_create)
        
        if files:
            uploaded_keys = []
            for f in files:
                key = await s3_service.upload_file_get_key(car_id=str(francheasy.id), file=f, folder="francheasy-photos")
                uploaded_keys.append(key)
            
            francheasy.s3_photo_francheasy_keys = uploaded_keys
            await db.commit()
            await db.refresh(francheasy)
        
        # Генерируем URL для фото
        photo_urls = []
        preview_photo_url = None
        keys = francheasy.s3_photo_francheasy_keys or []
        if keys:
            photo_urls = [await s3_service.generate_presigned_url(k) for k in keys]
            preview_photo_url = photo_urls[0] if photo_urls else None
        
        return FrancheasyResponse(
            id=francheasy.id,
            user_id=francheasy.user_id,
            title=francheasy.title,
            open_store=francheasy.open_store,
            start_capital=francheasy.start_capital,
            s3_photo_francheasy_keys=francheasy.s3_photo_francheasy_keys,
            photo_urls=photo_urls if photo_urls else None,
            preview_photo_url=preview_photo_url,
            created_at=francheasy.created_at,
            updated_at=francheasy.updated_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating francheasy: {str(e)}")

@francheasy_router.get("/list", response_model=List[FrancheasyResponse])
async def list_francheasy(
    db: AsyncSession = Depends(get_db),
):
    service = FrancheasyService(db)
    francheasy_list = await service.get_all_francheasy()
    
    enriched_francheasy = []
    for francheasy in francheasy_list:
        francheasy_data = {
            "id": francheasy.id,
            "user_id": francheasy.user_id,
            "title": francheasy.title,
            "open_store": francheasy.open_store,
            "start_capital": francheasy.start_capital,
            "s3_photo_francheasy_keys": francheasy.s3_photo_francheasy_keys,
            "created_at": francheasy.created_at,
            "updated_at": francheasy.updated_at,
        }
        try:
            keys = francheasy.s3_photo_francheasy_keys or []
            if keys:
                francheasy_data["photo_urls"] = [await s3_service.generate_presigned_url(k) for k in keys]
                francheasy_data["preview_photo_url"] = francheasy_data["photo_urls"][0]
        except Exception:
            pass
        
        enriched_francheasy.append(francheasy_data)
    
    return enriched_francheasy

@francheasy_router.get("/user", response_model=List[FrancheasyResponse])
async def list_my_francheasy(
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = FrancheasyService(db)
    francheasy_list = await service.get_francheasy_by_user(str(current_user.id))
    
    enriched_francheasy = []
    for francheasy in francheasy_list:
        francheasy_data = {
            "id": francheasy.id,
            "user_id": francheasy.user_id,
            "title": francheasy.title,
            "open_store": francheasy.open_store,
            "start_capital": francheasy.start_capital,
            "s3_photo_francheasy_keys": francheasy.s3_photo_francheasy_keys,
            "created_at": francheasy.created_at,
            "updated_at": francheasy.updated_at,
        }
        try:
            keys = francheasy.s3_photo_francheasy_keys or []
            if keys:
                francheasy_data["photo_urls"] = [await s3_service.generate_presigned_url(k) for k in keys]
                francheasy_data["preview_photo_url"] = francheasy_data["photo_urls"][0]
        except Exception:
            pass
        enriched_francheasy.append(francheasy_data)
    return enriched_francheasy

@francheasy_router.get("/{francheasy_id}", response_model=FrancheasyResponse)
async def get_francheasy_by_id(
    francheasy_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = FrancheasyService(db)
    francheasy = await service.get_francheasy_by_id(francheasy_id)
    
    if not francheasy:
        raise HTTPException(status_code=404, detail="Francheasy not found")
    
    francheasy_data = {
        "id": francheasy.id,
        "user_id": francheasy.user_id,
        "title": francheasy.title,
        "open_store": francheasy.open_store,
        "start_capital": francheasy.start_capital,
        "s3_photo_francheasy_keys": francheasy.s3_photo_francheasy_keys,
        "created_at": francheasy.created_at,
        "updated_at": francheasy.updated_at,
    }
    try:
        keys = francheasy.s3_photo_francheasy_keys or []
        if keys:
            francheasy_data["photo_urls"] = [await s3_service.generate_presigned_url(k) for k in keys]
            francheasy_data["preview_photo_url"] = francheasy_data["photo_urls"][0]
    except Exception:
        pass
    
    return francheasy_data

@francheasy_router.put("/{francheasy_id}", response_model=FrancheasyUpdateResponse)
async def update_francheasy(
    francheasy_id: str,
    francheasy_update: FrancheasyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = FrancheasyService(db)
    
    francheasy = await service.get_francheasy_by_id(francheasy_id)
    if not francheasy:
        raise HTTPException(status_code=404, detail="Francheasy not found")
    
    if francheasy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = {k: v for k, v in francheasy_update.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    try:
        updated_francheasy = await service.update_francheasy(francheasy_id, update_data)
        
        return FrancheasyUpdateResponse(
            id=updated_francheasy.id,
            user_id=updated_francheasy.user_id,
            updated_at=updated_francheasy.updated_at,
            message="Francheasy updated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating francheasy: {str(e)}")

@francheasy_router.delete("/{francheasy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_francheasy(
    francheasy_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = FrancheasyService(db)
    
    francheasy = await service.get_francheasy_by_id(francheasy_id)
    if not francheasy:
        raise HTTPException(status_code=404, detail="Francheasy not found")
    
    if francheasy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        await service.delete_francheasy(francheasy_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting francheasy: {str(e)}")


@francheasy_router.post("/{francheasy_id}/photos")
async def add_francheasy_photos(
    francheasy_id: str,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = FrancheasyService(db)
    francheasy = await service.get_francheasy_by_id(francheasy_id)
    if not francheasy:
        raise HTTPException(status_code=404, detail="Francheasy not found")

    if francheasy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    added_keys: list[str] = []
    for f in files:
        key = await s3_service.upload_file_get_key(car_id=francheasy_id, file=f, folder="francheasy-photos")
        added_keys.append(key)

    existing = francheasy.s3_photo_francheasy_keys or []
    francheasy.s3_photo_francheasy_keys = existing + added_keys
    await db.commit()

    all_keys = francheasy.s3_photo_francheasy_keys or []
    photo_urls = []
    for k in all_keys:
        try:
            photo_urls.append(await s3_service.generate_presigned_url(k))
        except Exception:
            continue

    preview_url = photo_urls[0] if photo_urls else None

    return {
        "francheasy_id": francheasy_id,
        "added": len(added_keys),
        "total": len(all_keys),
        "preview_photo_url": preview_url,
        "photo_urls": photo_urls,
    }
