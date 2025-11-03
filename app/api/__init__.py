from fastapi import APIRouter
from app.api import auth,user,francheasy,store,povilions

api_router =  APIRouter()

api_router.include_router(auth.auth_router,prefix="/auth",tags=["auth"])
api_router.include_router(user.user_router,prefix="/user",tags=["user"])
api_router.include_router(francheasy.francheasy_router,prefix="/francheasy",tags=["francheasy"])
api_router.include_router(store.store_router,prefix="/store",tags=["store"])
api_router.include_router(povilions.povilions_router,prefix="/povilions",tags=["povilions"])
__all__ = ["api_router"]