import json
from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx
from loguru import logger
import pkce
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.models.users import Users
from app.schemas.token import Token
from app.schemas.user import User_Data
from app.services.user_service import UserService
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    refresh_access_token,
    get_current_user,
)
import json

user_router = APIRouter()

@user_router.get("/profile", response_model=User_Data)
async def get_profile(current_user: Users = Depends(get_current_user)):    
    vk_json_parsed = None
    if current_user.vk_json:
        try:
            if isinstance(current_user.vk_json, dict):
                vk_json_parsed = current_user.vk_json
            else:
                vk_json_parsed = json.loads(current_user.vk_json)
        except (json.JSONDecodeError, TypeError):
            vk_json_parsed = None
    
    return User_Data(
        id=current_user.id,
        vk_id=current_user.vk_id,
        vk_json=vk_json_parsed,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
