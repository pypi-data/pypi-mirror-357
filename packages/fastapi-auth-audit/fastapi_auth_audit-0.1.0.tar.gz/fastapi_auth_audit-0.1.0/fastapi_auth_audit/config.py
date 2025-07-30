from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    AUDIT_TABLE_NAME: str = "audit_logs"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
