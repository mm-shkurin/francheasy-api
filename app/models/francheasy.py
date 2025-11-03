from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid
from sqlalchemy import Boolean, Column,Float, DateTime, ForeignKey, Integer,JSON, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from datetime import datetime

class Francheasy(Base):
    __tablename__ = "francheasy"
    title = Column(String)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    ebitda = Column(Float,nullable=False)
    start_capital = Column(Float,nullable=False)
    open_store = Column(Float,nullable=False)
    phone_number = Column(String,nullable=False)
    s3_photo_francheasy_keys = Column(JSON, default=[])
    
    businesses = relationship("Business", back_populates="francheasy")

    created_at = Column(DateTime, server_default=func.now()) 
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())