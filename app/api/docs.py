from fastapi import APIRouter, Request, Form, Depends, HTTPException, status, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.templating import Jinja2Templates
from app.core.config import DocsSettings
from app.services.session_service import session_service


docs_router = APIRouter()
docs_settings = DocsSettings()
templates = Jinja2Templates(directory="app/templates")

@docs_router.get("/docs", include_in_schema=False)
async def docs_login_page(request: Request):
    return templates.TemplateResponse(
        "docs/login.html",
        {"request": request, "title": "Swagger UI", "action": "/docs/auth"}
    )

@docs_router.post("/docs/auth", include_in_schema=False)
async def docs_auth(request: Request, api_key: str = Form()):
    if api_key == docs_settings.docs_api_key:
        session_token = session_service.create_session_token()
        session_service.add_session(session_token)
        response = RedirectResponse(url="/docs/swagger", status_code=302)
        response.set_cookie(key="docs_session", value=session_token, httponly=True)
        return response
    else:
        return templates.TemplateResponse(
            "docs/error.html",
            {"request": request, "error_message": "Неверный API ключ!", "redirect_url": "/docs"},
            status_code=401
        )

@docs_router.get("/docs/swagger", include_in_schema=False)
async def get_swagger_ui_documentation(request: Request):
    session_token = request.cookies.get("docs_session")
    if not session_token or not session_service.is_valid_session(session_token):
        return RedirectResponse(url="/docs", status_code=302)
    
    return get_swagger_ui_html(
        openapi_url="/openapi.json", 
        title="Absolute API - Swagger UI"
    )

@docs_router.get("/redoc", include_in_schema=False)
async def redoc_login_page(request: Request):
    return templates.TemplateResponse(
        "docs/login.html",
        {"request": request, "title": "ReDoc", "action": "/redoc/auth"}
    )

@docs_router.post("/redoc/auth", include_in_schema=False)
async def redoc_auth(request: Request, api_key: str = Form()):
    if api_key == docs_settings.docs_api_key:
        session_token = session_service.create_session_token()
        session_service.add_session(session_token)
        response = RedirectResponse(url="/redoc/view", status_code=302)
        response.set_cookie(key="docs_session", value=session_token, httponly=True)
        return response
    else:
        return templates.TemplateResponse(
            "docs/error.html",
            {"request": request, "error_message": "Неверный API ключ!", "redirect_url": "/redoc"},
            status_code=401
        )

@docs_router.get("/redoc/view", include_in_schema=False)
async def get_redoc_documentation(request: Request):
    session_token = request.cookies.get("docs_session")
    if not session_token or not session_service.is_valid_session(session_token):
        return RedirectResponse(url="/redoc", status_code=302)
    
    return get_redoc_html(
        openapi_url="/openapi.json", 
        title="Absolute API - ReDoc"
    )

@docs_router.get("/openapi.json", include_in_schema=False)
async def get_openapi_schema(request: Request):
    
    session_token = request.cookies.get("docs_session")
    if session_token and session_service.is_valid_session(session_token):

        from fastapi.openapi.utils import get_openapi
        from app.main import app
        
        return get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
    
    api_key = request.headers.get("X-API-Key")
    if api_key and api_key == docs_settings.docs_api_key:
        from fastapi.openapi.utils import get_openapi
        from app.main import app
        
        return get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
    
    raise HTTPException(status_code=401, detail="Unauthorized")