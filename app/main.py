from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import init_db
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", description="AI-powered 7-day fitness plan generator based on the supplied FitBuddy specification.", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "../static"), name="static")
app.include_router(router)
