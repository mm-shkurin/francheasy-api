from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.francheasy import Francheasy
from app.schemas.francheasy import FrancheasyCreate, FrancheasyUpdate
from typing import List, Optional
import uuid


class FrancheasyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_sale_car(
        self,
        user_id: str,
        payload: FrancheasyCreate,
    ) -> Francheasy:
        sale_car = SaleCars(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            title=payload.title,
            phone_number=payload.phone_number,
            ebitda=payload.ebitda,
            start_capital=payload.start_capital,
            open_store=payload.open_store,
            s3_photo_francheasy_keys=payload.photos_b64 or [],
        )
        self.db.add(francheasy)
        await self.db.commit()
        await self.db.refresh(francheasy)
        return francheasy

    async def get_francheasy_by_id(self, francheasy_id: str) -> Optional[Francheasy]:
        res = await self.db.execute(
            select(Francheasy).where(Francheasy.id == uuid.UUID(francheasy_id))
        )
        return res.scalar_one_or_none()

    async def get_francheasy_by_user(self, user_id: str) -> List[Francheasy]:
        res = await self.db.execute(
            select(Francheasy).where(Francheasy.user_id == uuid.UUID(user_id))
        )
        return list(res.scalars().all())

    async def get_all_francheasy(self) -> List[Francheasy]:
        res = await self.db.execute(
            select(Francheasy).order_by(Francheasy.created_at.desc())
        )
        return list(res.scalars().all())

    async def add_francheasy_photos(self, francheasy_id: str, photos_b64: List[str]) -> Francheasy:
        francheasy = await self.get_francheasy_by_id(francheasy_id)
        if not sale_car:
            raise ValueError("Francheasy not found")
        existing = francheasy.s3_photo_francheasy_keys or []
        francheasy.s3_photo_francheasy_keys = existing + list(photos_b64)
        await self.db.commit()
        await self.db.refresh(francheasy)
        return francheasy

    async def update_francheasy(self, francheasy_id: str, update_data: dict) -> Francheasy:
        francheasy = await self.get_francheasy_by_id(francheasy_id)
        if not francheasy:
            raise ValueError("Francheasy not found")
        
        if "phone_number" in update_data and update_data["phone_number"] is not None:
            francheasy.phone_number = update_data["phone_number"]
        if "ebitda" in update_data and update_data["ebitda"] is not None:
            francheasy.ebitda = update_data["ebitda"]
        if "start_capital" in update_data and update_data["start_capital"] is not None:
            francheasy.start_capital = update_data["start_capital"]
        if "open_store" in update_data and update_data["open_store"] is not None:
            francheasy.open_store = update_data["open_store"]
        if "title" in update_data and update_data["title"] is not None:
            francheasy.title = update_data["title"]
        await self.db.commit()
        await self.db.refresh(francheasy)
        
        if francheasy.chroma_document_id:
            try:
                from app.services.chromadb_service import ChromaService
                chroma = ChromaService()
                
                current_data = await chroma.get_document(francheasy.chroma_document_id)
                if current_data and isinstance(current_data, dict):
                    updated_data = current_data.copy()
                    for key, value in update_data.items():
                        if value is not None and key != "vin":  
                            updated_data[key] = value
                    
                    await chroma.update_document(francheasy.chroma_document_id, updated_data)
            except Exception as e:
                print(f"Error updating ChromaDB for francheasy {francheasy_id}: {e}")
        
        return francheasy

    async def delete_francheasy(self, francheasy_id: str) -> bool:
        francheasy = await self.get_francheasy_by_id(francheasy_id)
        if not francheasy:
            raise ValueError("Francheasy not found")

        if francheasy.chroma_document_id:
            try:
                from app.services.chromadb_service import ChromaService

                chroma = ChromaService()
                await chroma.delete_document(francheasy.chroma_document_id)
            except Exception:
                pass

        await self.db.execute(
            delete(Francheasy).where(Francheasy.id == uuid.UUID(francheasy_id))
        )
        await self.db.commit()
        return True