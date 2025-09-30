from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.api.v1.transactions import router as transactions_router
from app.api.v1.summary import router as summary_router
from app.web.routes import router as web_router
from app.core.database import Base, engine
import app.core.models  # ensure models are imported

app = FastAPI(title="Monthly Spending Tracker")

# Static files
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# CORS (allow local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup (dev convenience)
@app.on_event("startup")
async def on_startup():
    Base.metadata.create_all(bind=engine)

# API routers
app.include_router(transactions_router)
app.include_router(summary_router)

# Web routes
app.include_router(web_router)


@app.get("/healthz")
async def healthz():
    return {"ok": True}
