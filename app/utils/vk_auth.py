import hashlib
import hmac
import httpx
import json

from fastapi import Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
import pkce 
from app.core.config import VKSettings
from app.db.database import get_db
from app.utils.security import create_access_token, create_refresh_token
from app.services.pkce_service import PKCEService
vk_auth_settings = VKSettings()
pkce_service = PKCEService()

async def get_vk_user_info(access_token: str, user_id: int = None):
    vk_api_url = str(vk_auth_settings.vk_api_url)
    params = {
        "access_token": access_token,
        "v": "5.199",
        "fields": "first_name,last_name,photo_200,domain",
    }
    
    if user_id:
        params["user_ids"] = user_id
    else:
        params["user_ids"] = ""

    async with httpx.AsyncClient() as client:
        response = await client.get(vk_api_url, params=params)
        data = response.json()

        if "error" in data:
            error = data["error"]
            raise HTTPException(
                status_code=400,
                detail=f"VK API error: {error.get('error_msg', 'Unknown error')}",
            )

        return data.get("response", [{}])[0]

async def generate_auth_url() -> tuple[str,str]:
    code_verifier,code_challenge = pkce.generate_pkce_pair()
    logger.debug("Generated PKCE pair")

    session_id = await pkce_service.store_pkce_pair(code_verifier,code_challenge)
    logger.debug("Stored PKCE pair for session")

    state = session_id  
    logger.debug("Generated state for VK auth")

    auth_url = f"{vk_auth_settings.vk_auth_url}?app_id={vk_auth_settings.vk_client_id}&response_type=code&redirect_uri={vk_auth_settings.vk_redirect_uri}&scope=user_id%20first_name%20last_name%20avatar&lang_id=3&scheme=space_gray&oauth_version=2&state={state}&code_challenge={code_challenge}&code_challenge_method=sha256"

    return auth_url,session_id

async def validate_callback(code: str, state: str, device_id: str = None) -> tuple[str,str]:
    logger.debug("Validating VK callback")
    session_id = state  
    logger.debug("Derived session_id from state")

    pkce_data = await pkce_service.get_pkce_pair(session_id)
    logger.debug("PKCE data fetched from Redis: %s", bool(pkce_data))

    if not pkce_data:
        logger.error("No PKCE data found for session")
        raise HTTPException(status_code = 400, detail="Invalid state")

    code_verifier = pkce_data["verifier"]
    logger.debug("Extracted code_verifier")

    await pkce_service.delete_pkce_pair(session_id)
    logger.debug("Deleted PKCE pair from Redis")

    logger.debug("Calling exchange_code_for_token")
    access_token, user_id = await exchange_code_for_token(code, code_verifier, device_id)
    logger.info("VK token exchange succeeded")
    logger.debug("Got user_id from token: %s", user_id)

    return code_verifier, access_token, user_id

async def exchange_code_for_token(code: str, code_verifier: str, device_id: str = None) -> tuple[str, int]:
    logger.debug("Exchanging VK code for token")
    
    token_url = str(vk_auth_settings.vk_oauth_url)
    logger.debug("VK token URL prepared")

    data = {
        "grant_type": "authorization_code",
        "client_id": vk_auth_settings.vk_client_id,
        "client_secret": vk_auth_settings.vk_client_secret,
        "redirect_uri": str(vk_auth_settings.vk_redirect_uri),
        "code_verifier": code_verifier,
        "code": code,
    }
    
    if device_id:
        data["device_id"] = device_id
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    safe_data = {k: ('***' if k in {"client_secret", "code", "device_id"} else v) for k, v in data.items()}
    logger.debug("Making request to VK with data: %s", safe_data)

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, headers=headers, data=data)
        logger.debug("VK response status: %s", response.status_code)
        
        token_data = response.json()
        logger.debug("VK token data keys: %s", list(token_data.keys()))
        
        access_token = token_data.get("access_token")
        user_id = token_data.get("user_id")
        
        if not access_token:
            error_msg = token_data.get("error", "Unknown error")
            logger.error("No access token in VK response: %s", error_msg)
            raise HTTPException(
                status_code=400, detail=f"Invalid token response from VK: {error_msg}"
            )
        
        logger.debug("Got user_id from VK response")
        return access_token, user_id

async def vk_auth(user_info, id, db: AsyncSession):
    credentials_exception = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Could not proof youre VK session",
    )
    
    access_token = await create_access_token({"id": str(id)})
    refresh_token = await create_refresh_token({"id": str(id)})
    
    return refresh_token, access_token
