from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid
from sqlalchemy import Column, ForeignKey, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime


class BusinessRequest(Base):
    __tablename__ = "business_requests"
    
    request_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    francheasy_id = Column(UUID(as_uuid=True), ForeignKey("francheasy.id"), nullable=False)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.store_id"), nullable=True)
    povilion_id = Column(UUID(as_uuid=True), ForeignKey("povilions.povilion_id"), nullable=True)
    status = Column(String, default="pending", nullable=False)
    
    user = relationship("Users", back_populates="business_requests")
    francheasy = relationship("Francheasy", back_populates="business_requests")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

