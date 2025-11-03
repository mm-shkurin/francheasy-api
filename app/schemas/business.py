from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class TransactionCreate(BaseModel):
    type: TransactionType
    amount: float = Field(..., ge=0)
    description: Optional[str] = None


class TransactionRead(BaseModel):
    type: str
    amount: float
    description: Optional[str] = None
    date: datetime


class BusinessBase(BaseModel):
    francheasy_id: UUID
    store_id: Optional[UUID] = None
    povilion_id: Optional[UUID] = None


class BusinessCreate(BusinessBase):
    pass


class BusinessRead(BusinessBase):
    business_id: UUID
    user_id: UUID
    transactions: List[TransactionRead] = []
    total_income: float = 0.0
    total_expense: float = 0.0
    balance: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BusinessListItem(BaseModel):
    business_id: UUID
    francheasy_id: UUID
    store_id: Optional[UUID] = None
    povilion_id: Optional[UUID] = None
    total_income: float = 0.0
    total_expense: float = 0.0
    balance: float = 0.0
    
    class Config:
        from_attributes = True

