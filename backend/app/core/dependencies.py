from typing import Generator
from app.core.database import SessionLocal
from app.core.config import APP_API_KEY
from fastapi import HTTPException, Depends, Header, status

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    if not APP_API_KEY: return
    if x_api_key != APP_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return x_api_key