from .api import api_router
from .main import app

app.include_router(api_router)
