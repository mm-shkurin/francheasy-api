from fastapi import APIRouter
from app.api import auth,user

api_router =  APIRouter()

api_router.include_router(auth.auth_router,prefix="/auth",tags=["auth"])
api_router.include_router(user.user_router,prefix="/user",tags=["user"])

__all__ = ["api_router"]