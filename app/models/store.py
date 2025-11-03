from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid
from sqlalchemy import  Column, ForeignKey,String, Text,DateTime,Float, func
from sqlalchemy.dialects.postgresql import JSONB, UUID,ARRAY
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

class Store(Base):
    __tablename__ = "stores"
    store_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String,nullable=False)
    cross_country_ability = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    adress = Column(String,nullable=True)
    
    user = relationship("Users", back_populates="stores")
    povilions = relationship("Povilions", back_populates="store")
    businesses = relationship("Business", back_populates="store")

    created_at = Column(DateTime, server_default=func.now()) 
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())