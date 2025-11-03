from app.models import users, francheasy, store, povilions, business

from .api import api_router
from .main import app

app.include_router(api_router)
