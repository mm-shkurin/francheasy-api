from fastapi import APIRouter
from app.api import auth,user,francheasy

api_router =  APIRouter()

api_router.include_router(auth.auth_router,prefix="/auth",tags=["auth"])
api_router.include_router(user.user_router,prefix="/user",tags=["user"])
api_router.include_router(francheasy.francheasy_router,prefix="/francheasy",tags=["francheasy"])
__all__ = ["api_router"]