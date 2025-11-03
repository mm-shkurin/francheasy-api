from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class PovilionsBase(BaseModel):
    store_id: UUID
    title: str
    price: float = Field(..., ge=0)


class PovilionsCreate(PovilionsBase):
    pass


class PovilionsUpdate(BaseModel):
    title: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    
    class Config:
        from_attributes = True


class PovilionsRead(PovilionsBase):
    povilion_id: UUID
    user_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PovilionsListItem(BaseModel):
    povilion_id: UUID
    store_id: UUID
    title: str
    price: float
    
    class Config:
        from_attributes = True

