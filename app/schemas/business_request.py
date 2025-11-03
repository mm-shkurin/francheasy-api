from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class RequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class BusinessRequestCreate(BaseModel):
    francheasy_id: UUID
    store_id: Optional[UUID] = None
    povilion_id: Optional[UUID] = None


class BusinessRequestUpdate(BaseModel):
    status: RequestStatus


class BusinessRequestRead(BaseModel):
    request_id: UUID
    user_id: UUID
    francheasy_id: UUID
    store_id: Optional[UUID] = None
    povilion_id: Optional[UUID] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BusinessRequestListItem(BaseModel):
    request_id: UUID
    user_id: UUID
    francheasy_id: UUID
    francheasy_title: Optional[str] = None
    store_id: Optional[UUID] = None
    store_title: Optional[str] = None
    povilion_id: Optional[UUID] = None
    povilion_title: Optional[str] = None
    povilion_price: Optional[float] = None
    status: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

