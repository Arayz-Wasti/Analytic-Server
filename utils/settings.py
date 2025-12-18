import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()


class Settings:
    """
    Centralized application configuration.
    """

    # MongoDB
    MONGO_URI: str = os.getenv(
        "MONGO_URI",
        "mongodb://localhost:27017"
    )
    DB_NAME: str = os.getenv(
        "DB_NAME",
        "analytic_server"
    )

    # App metadata
    APP_NAME: str = "Analytics Server"
    ENV: str = os.getenv("ENV", "local")

    # JWT
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_secret: str = os.getenv("JWT_SECRET", "")
    jwt_access_expires: int = int(os.getenv("JWT_ACCESS_EXPIRES"))
    jwt_refresh_expires: int = int(os.getenv("JWT_REFRESH_EXPIRES", 2592000))

    SMTP_HOST: str = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 465))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SMTP_FROM: str = os.getenv("SMTP_FROM")

    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY")


@lru_cache
def get_settings() -> Settings:
    return Settings()
