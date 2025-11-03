from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import BaseModel, validator   
import json

class User_Data(BaseModel):
    id: UUID
    vk_id: Optional[str] = None
    vk_json: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True