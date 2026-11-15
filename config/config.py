import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    MAX_CONTENT_LENGTH = int(
        os.getenv("MAX_CONTENT_LENGTH", 20971520)
    )

    DATABASE_URL = os.getenv("DATABASE_URL")

    ENVIRONMENT = os.getenv(
        "APP_ENV",
        "development"
    )

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    SESSION_COOKIE_SECURE = (
        ENVIRONMENT == "production"
    )