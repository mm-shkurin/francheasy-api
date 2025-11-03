from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from app.models.business_request import BusinessRequest
from app.models.francheasy import Francheasy
from app.schemas.business_request import BusinessRequestCreate, BusinessRequestUpdate, RequestStatus
from uuid import UUID
from typing import List, Optional


class BusinessRequestService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_request(self, user_id: UUID, request_in: BusinessRequestCreate) -> BusinessRequest:
        from app.services.francheasy import FrancheasyService
        francheasy_service = FrancheasyService(self.db)
        francheasy = await francheasy_service.get_francheasy_by_id(str(request_in.francheasy_id))
        if not francheasy:
            raise ValueError("Francheasy not found")
        
        db_request = BusinessRequest(
            user_id=user_id,
            francheasy_id=request_in.francheasy_id,
            store_id=request_in.store_id,
            povilion_id=request_in.povilion_id,
            status="pending"
        )
        self.db.add(db_request)
        try:
            await self.db.commit()
            await self.db.refresh(db_request)
            return db_request
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError(f"Ошибка при создании запроса: {e}")

    async def get_request_by_id(self, request_id: UUID) -> Optional[BusinessRequest]:
        result = await self.db.execute(select(BusinessRequest).where(BusinessRequest.request_id == request_id))
        return result.scalar_one_or_none()

    async def get_requests_by_francheasy_owner(self, owner_user_id: UUID) -> List[BusinessRequest]:
        result = await self.db.execute(
            select(BusinessRequest)
            .join(Francheasy, BusinessRequest.francheasy_id == Francheasy.id)
            .where(Francheasy.user_id == owner_user_id)
        )
        return list(result.scalars().all())

    async def get_requests_by_user(self, user_id: UUID) -> List[BusinessRequest]:
        result = await self.db.execute(select(BusinessRequest).where(BusinessRequest.user_id == user_id))
        return list(result.scalars().all())

    async def update_request_status(
        self, 
        request_id: UUID, 
        francheasy_owner_id: UUID,
        status_update: BusinessRequestUpdate
    ) -> Optional[BusinessRequest]:
        request = await self.get_request_by_id(request_id)
        if not request:
            return None
        
        from app.services.francheasy import FrancheasyService
        francheasy_service = FrancheasyService(self.db)
        francheasy = await francheasy_service.get_francheasy_by_id(str(request.francheasy_id))
        if not francheasy or francheasy.user_id != francheasy_owner_id:
            raise ValueError("Not authorized to update this request")
        
        await self.db.execute(
            update(BusinessRequest)
            .where(BusinessRequest.request_id == request_id)
            .values(status=status_update.status.value)
        )
        await self.db.commit()
        
        if status_update.status == RequestStatus.APPROVED:
            from app.services.business_service import BusinessService
            from app.schemas.business import BusinessCreate
            business_service = BusinessService(self.db)
            business_create = BusinessCreate(
                francheasy_id=request.francheasy_id,
                store_id=request.store_id,
                povilion_id=request.povilion_id
            )
            await business_service.create_business(request.user_id, business_create)
        
        return await self.get_request_by_id(request_id)

    async def delete_request(self, request_id: UUID) -> bool:
        from sqlalchemy import delete
        result = await self.db.execute(delete(BusinessRequest).where(BusinessRequest.request_id == request_id))
        await self.db.commit()
        return result.rowcount > 0

