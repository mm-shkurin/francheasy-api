# Импорт моделей для инициализации SQLAlchemy relationships
from app.models import users, francheasy, store, povilions

from .api import api_router
from .main import app

app.include_router(api_router)
