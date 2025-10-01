from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.openapi.utils import get_openapi

from app.api.v1.transactions import router as transactions_router
from app.api.v1.summary import router as summary_router
from app.web.routes import router as web_router
from app.core.database import Base, engine
import app.core.models  # ensure models are imported

app = FastAPI(title="Monthly Spending Tracker", swagger_ui_parameters={"persistAuthorization": True})

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


# Add OpenAPI security scheme for API key header so Swagger shows Authorize button
@app.get("/openapi.json")
async def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description="Monthly Spending Tracker API",
        routes=app.routes,
    )
    components = openapi_schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    security_schemes["ApiKeyAuth"] = {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
    }
    # Don't apply security globally - let individual routes handle it
    app.openapi_schema = openapi_schema
    return app.openapi_schema
