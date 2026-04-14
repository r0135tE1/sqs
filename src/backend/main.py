import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, flags, highscores
from app.services.flag_cache import flag_cache

logger = logging.getLogger(__name__)

#API-Startup: cache Flags and run Server
@asynccontextmanager
async def lifespan(app: FastAPI):
    await flag_cache.load()
    yield


app = FastAPI(
    title="Fun with Flags API",
    description="Backend for the Fun with Flags flag-guessing game.",
    version="0.1.0",
    lifespan=lifespan,
)

#Middelware allowing CORS for Backend-Frontend Communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flags.router)
app.include_router(auth.router)
app.include_router(highscores.router)

# Endpoint for Monitoring
@app.get("/health", tags=["metadata"])
async def health():
    return {"status": "ok", "flags_cached": flag_cache.count()}
