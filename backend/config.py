import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = "AZ Turf-Pro API"
    VERSION = "1.0.0"
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./az_turf.db"
    )

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "AZ-TURF-PRO-SECURE-KEY"
    )

settings = Settings()
