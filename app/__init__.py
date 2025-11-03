from app.models import users, francheasy, store, povilions, business, business_request

from .api import api_router
from .main import app

app.include_router(api_router)
