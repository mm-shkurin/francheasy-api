from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid
from sqlalchemy import Column, ForeignKey, String, DateTime, func, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime


class Business(Base):
    __tablename__ = "business"
    
    business_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    francheasy_id = Column(UUID(as_uuid=True), ForeignKey("francheasy.id"), nullable=False)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.store_id"), nullable=True)
    povilion_id = Column(UUID(as_uuid=True), ForeignKey("povilions.povilion_id"), nullable=True)
    
    transactions = Column(JSON, default=[])
    
    user = relationship("Users", back_populates="businesses")
    francheasy = relationship("Francheasy", back_populates="businesses")
    store = relationship("Store", back_populates="businesses")
    povilion = relationship("Povilions", back_populates="business")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

