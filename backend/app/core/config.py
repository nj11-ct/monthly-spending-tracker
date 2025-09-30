import os

DB_URL = os.getenv("DATABASE_URL", "sqlite:///app/app.db")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
