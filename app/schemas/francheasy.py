from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class FrancheasyCreate(BaseModel):
    phone_number: str
    ebitda: float
    start_capital: float
    open_store: float
    title: Optional[str] = None
    photos_b64: Optional[List[str]] = None


class FrancheasyUpdate(BaseModel):
    phone_number: Optional[str] = None
    ebitda: Optional[float] = None
    start_capital: Optional[float] = None
    open_store: Optional[float] = None
    title: Optional[str] = None
    photos_b64: Optional[List[str]] = None


class FrancheasyUpdateResponse(BaseModel):
    id: UUID
    user_id: UUID
    chroma_document_id: Optional[str]
    updated_at: datetime
    message: str = "Francheasy updated successfully"

    class Config:
        from_attributes = True


class FrancheasyResponse(BaseModel):
    id: UUID
    user_id: UUID
    chroma_document_id: Optional[str]
    s3_photo_francheasy_keys: Optional[List[str]] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
