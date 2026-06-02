import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, game, highscores
from app.services.flag_cache import flag_cache
from app.services.game_session import game_session_store

logger = logging.getLogger(__name__)

_SESSION_TTL_SECONDS = 12 * 3600
_CLEANUP_INTERVAL_SECONDS = 3600


async def _session_cleanup_task() -> None:
    while True:
        await asyncio.sleep(_CLEANUP_INTERVAL_SECONDS)
        removed = game_session_store.cleanup_expired(_SESSION_TTL_SECONDS)
        if removed:
            logger.info("Cleaned up %d expired game sessions", removed)


#API-Startup: cache Flags and run Server
@asynccontextmanager
async def lifespan(app: FastAPI):
    await flag_cache.load()
    task = asyncio.create_task(_session_cleanup_task())
    yield
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)


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

app.include_router(auth.router)
app.include_router(game.router)
app.include_router(highscores.router)

# Endpoint for Monitoring
@app.get("/health", tags=["metadata"])
async def health():
    return {"status": "ok", "flags_cached": flag_cache.count()}
