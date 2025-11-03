from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid
from sqlalchemy import  Column, ForeignKey,String, Text,DateTime,Float, func
from sqlalchemy.dialects.postgresql import JSONB, UUID,ARRAY
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

class Povilions(Base):
    __tablename__ = "povilions"
    povilion_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.store_id"), nullable=False)
    title = Column(String,nullable=False)
    price = Column(Float, nullable=False)
    
    user = relationship("Users", back_populates="povilions")
    store = relationship("Store", back_populates="povilions")
    business = relationship("Business", back_populates="povilion")

    created_at = Column(DateTime, server_default=func.now()) 
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())