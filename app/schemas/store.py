from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class PovilionListItem(BaseModel):
    povilion_id: UUID
    title: str
    price: float

class StoreBase(BaseModel):
    title: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    cross_country_ability: float
    adress: str

class StoreCreate(StoreBase):
    pass

class StoreUpdate(BaseModel):
    title: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    cross_country_ability: Optional[float] = None
    adress : Optional[str] = None
    class Config:
        from_attributes = True

class StoreRead(StoreBase):
    store_id: UUID
    user_id: UUID
    povilions: Optional[List[PovilionListItem]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class StoreListItem(BaseModel):
    store_id: UUID
    title: Optional[str] = None
    adress: Optional[str] = None
    cross_country_ability: Optional[float] = None
    latitude: float
    longitude: float