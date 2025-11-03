import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.core.config import AppSettings
from app.core.config import CORSSettings
from loguru import logger
from app.api.auth import auth_router
from app.api.docs import docs_router

sys.path.append('/app')

def get_logger():
    settings = get_app_settings()
    logger.add(
        settings.log_file,
        rotation = settings.log_rotation,
        compression = settings.log_compression.value,
        format = settings.log_format,
    )

def get_app_settings() -> AppSettings:
    try:
        return AppSettings()
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        logger.error(f"Using default settings")
        return AppSettings()

def setup_logging():
    settings = get_app_settings()
    logger.add(
        settings.log_file,
        rotation=settings.log_rotation,
        compression=settings.log_compression.value,
        format=settings.log_format,
    )
def create_app():
    settings = get_app_settings() 
    app = FastAPI(
        title=settings.app_name,
        description="API for Francheasy application",
        version="1.0.0",
        docs_url=None,  
        redoc_url=None,
        openapi_url=None  
    )
    setup_logging()
    # CORS
    try:
        cors_settings = CORSSettings()
        origins = [o.strip() for o in cors_settings.cors_origins.split(",") if o.strip()]
        if origins:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
    except Exception:
        pass
    
    @app.get("/")
    def read_root():
        return {"message": "Welcome to API Francheasy"}
    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
    app.include_router(auth_router, prefix="/auth")
    app.include_router(docs_router)
    
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",  
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["."],
    )