import json
from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
from loguru import logger
import pkce
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import  VKSettings
from app.core.config import JWTSettings
from app.db.database import get_db
from app.models.users import Users
from app.schemas.token import Token
from app.schemas.user import User_Data
from app.services import user_service
from app.services.user_service import UserService
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    refresh_access_token,
)
from app.utils.vk_auth import generate_auth_url, validate_callback, get_vk_user_info, vk_auth
from fastapi import FastAPI, Request

auth_router = APIRouter()
vk_auth_settings = VKSettings()
templates = Jinja2Templates(directory="app/templates")
jwt_settings = JWTSettings()

@auth_router.get("/vk/login", response_class=RedirectResponse)
async def button_placeholders_vk():
    auth_url, session_id = await generate_auth_url()
    return RedirectResponse(auth_url)

@auth_router.get("/vk/callback")
async def vk_oauth_callback(
    request: Request, 
    db: AsyncSession = Depends(get_db)
):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")
    
    try:
        device_id = request.query_params.get("device_id")
        
        code_verifier, vk_access_token, vk_user_id = await validate_callback(code, state, device_id)
        
        vk_user_info = await get_vk_user_info(vk_access_token, vk_user_id)
        
        if not vk_user_info or not vk_user_info.get("id"):
            raise HTTPException(status_code=400, detail="Could not get user info from VK")
        vk_json = json.dumps(vk_user_info)
        
        user_service = UserService(db)
        user_id = await user_service.create_or_get_vk_user(
            vk_id=str(vk_user_info["id"]), 
            vk_json=vk_json
        )
        
        refresh_token, jwt_access_token = await vk_auth(vk_user_info, user_id, db)
        
        return Token(
            access_token=jwt_access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@auth_router.post("/refresh", response_model=Token)
async def refresh(refresh_token: str = Body(..., embed=True), db: AsyncSession = Depends(get_db)):
    new_access_token = await refresh_access_token(refresh_token)
    
    return Token(
        access_token=new_access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
