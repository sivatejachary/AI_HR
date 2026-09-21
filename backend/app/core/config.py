import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application & Environment
    APP_NAME: str = "Recruitment Pro Engine"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "recruitment_pro_enterprise_secret_key_2026")

    # Single Source of Truth Database Connection
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

    # Centralized URL Configuration (Internal vs. External)
    BACKEND_PUBLIC_URL: str = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8000")
    BACKEND_INTERNAL_URL: str = os.getenv("BACKEND_INTERNAL_URL", "http://localhost:8000")
    FRONTEND_PUBLIC_URL: str = os.getenv("FRONTEND_PUBLIC_URL", "http://localhost:3000")

    # n8n Automation Engine URLs
    N8N_PUBLIC_URL: str = os.getenv("N8N_PUBLIC_URL", "https://shivateja123.app.n8n.cloud")
    N8N_INTERNAL_URL: str = os.getenv("N8N_INTERNAL_URL", "https://shivateja123.app.n8n.cloud")
    N8N_INTEGRATION_API_KEY: str = os.getenv("N8N_INTEGRATION_API_KEY", "n8n_live_key_recruitmentpro_2026")

    # Google Cloud OAuth 2.0 Credentials (Project feisty-legend-450615-n5)
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "186843356614-2k28sqllqgf4fo2nk38mspuipnfssl9q.apps.googleusercontent.com")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "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")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/integrations/google/callback")
    GOOGLE_PROJECT_ID: str = os.getenv("GOOGLE_PROJECT_ID", "feisty-legend-450615-n5")

    # ElevenLabs Voice AI
    ELEVENLABS_API_KEY: Optional[str] = os.getenv("ELEVENLABS_API_KEY")
    ELEVENLABS_AGENT_ID: Optional[str] = os.getenv("ELEVENLABS_AGENT_ID")
    ELEVENLABS_WEBHOOK_URL: str = os.getenv("ELEVENLABS_WEBHOOK_URL", "http://localhost:8000/api/v1/calls/elevenlabs-webhook")

    # Redis & Vector Search
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    QDRANT_URL: Optional[str] = os.getenv("QDRANT_URL")

    # CORS Origins Configuration
    CORS_ORIGINS: List[str] = [
        o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000").split(",") if o.strip()
    ]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
