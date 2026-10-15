from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Deepfake Detection and Media Verification System", lifespan=lifespan)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Routers are added here as they are written, e.g.
#   from app.api import submissions
#   app.include_router(submissions.router, prefix="/api")

_static = Path(__file__).parent / "static"
if _static.exists():
    app.mount("/static", StaticFiles(directory=_static), name="static")
