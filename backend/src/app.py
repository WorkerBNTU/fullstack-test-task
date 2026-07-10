from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import alerts, files
from src.core.config import get_settings

settings = get_settings()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router)
app.include_router(alerts.router)
