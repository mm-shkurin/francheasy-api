from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Enum, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base
from datetime import datetime
from app.db.database import BaseModel
class Users(BaseModel):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vk_id = Column(String, unique=True, index=True)
    vk_json = Column(JSONB, nullable=True)
    stores = relationship("Store", back_populates="user")
    created_at = Column(DateTime, server_default=func.now()) 
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  