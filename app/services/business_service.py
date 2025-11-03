from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from app.models.business import Business
from app.schemas.business import BusinessCreate, TransactionCreate
from uuid import UUID
from typing import List, Optional
from datetime import datetime


class BusinessService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_business(self, user_id: UUID, business_in: BusinessCreate) -> Business:
        db_business = Business(
            user_id=user_id,
            francheasy_id=business_in.francheasy_id,
            store_id=business_in.store_id,
            povilion_id=business_in.povilion_id,
            transactions=[]
        )
        self.db.add(db_business)
        try:
            await self.db.commit()
            await self.db.refresh(db_business)
            return db_business
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError(f"Ошибка при создании бизнеса: {e}")

    async def get_business_by_id(self, business_id: UUID) -> Optional[Business]:
        result = await self.db.execute(select(Business).where(Business.business_id == business_id))
        return result.scalar_one_or_none()

    async def get_businesses_by_user(self, user_id: UUID) -> List[Business]:
        result = await self.db.execute(select(Business).where(Business.user_id == user_id))
        return list(result.scalars().all())

    async def get_businesses_by_francheasy(self, francheasy_id: UUID) -> List[Business]:
        result = await self.db.execute(select(Business).where(Business.francheasy_id == francheasy_id))
        return list(result.scalars().all())

    async def add_transaction(self, business_id: UUID, transaction: TransactionCreate) -> Optional[Business]:
        business = await self.get_business_by_id(business_id)
        if not business:
            return None
        
        new_transaction = {
            "type": transaction.type.value,
            "amount": transaction.amount,
            "description": transaction.description,
            "date": datetime.now().isoformat()
        }
        
        current_transactions = business.transactions if business.transactions else []
        current_transactions.append(new_transaction)
        
        await self.db.execute(
            update(Business)
            .where(Business.business_id == business_id)
            .values(transactions=current_transactions)
        )
        await self.db.commit()
        return await self.get_business_by_id(business_id)

    def calculate_totals(self, business: Business) -> dict:
        transactions = business.transactions if business.transactions else []
        
        total_income = 0.0
        total_expense = 0.0
        
        for transaction in transactions:
            if transaction.get("type") == "income":
                total_income += float(transaction.get("amount", 0))
            elif transaction.get("type") == "expense":
                total_expense += float(transaction.get("amount", 0))
        
        balance = total_income - total_expense
        
        total_amount = total_income + total_expense
        profit_percentage = (balance / total_amount * 100) if total_amount > 0 else 0.0
        
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
            "profit_percentage": round(profit_percentage, 2)
        }

    async def delete_business(self, business_id: UUID) -> bool:
        from sqlalchemy import delete
        result = await self.db.execute(delete(Business).where(Business.business_id == business_id))
        await self.db.commit()
        return result.rowcount > 0

