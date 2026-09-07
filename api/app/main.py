from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db

__version__ = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run alembic upgrade head on startup (best-effort for Slice 0)
    try:
        init_db()
    except Exception:
        # DB init is best-effort for health check (G7 local-first)
        pass
    yield


app = FastAPI(
    title="Minerva API",
    version=__version__,
    lifespan=lifespan,
)

# CORS for web (Vite dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "version": __version__}
