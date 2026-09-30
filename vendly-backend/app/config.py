from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    APP_ENV: str = "production"
    USE_MOCK_WHATSAPP: bool = False

    # --- Database ---
    # SQLite for local dev, Postgres (Neon) via DATABASE_URL for deploy.
    # Render's disk is ephemeral, so production MUST set DATABASE_URL.
    DATABASE_URL: str = "sqlite:///./vendly.db"

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:5173"

    # --- Ops / health ---
    PUBLIC_BASE_URL: str = "http://127.0.0.1:8000"
    APP_VERSION: str = "0.1.0"

    # --- Meta WhatsApp API Credentials ---
    WHATSAPP_VERIFY_TOKEN: str = "V3ndly_Wh4t5App_7ok3n_9fK2mQx8"
    WHATSAPP_PHONE_NUMBER_ID: str = "1426941730493435"
    WHATSAPP_ACCESS_TOKEN: str = "EAANkxqqBgOQBSi2pJiaAnGSKbSLkoAfjuJhuHDLZBEfdbvCZAZBnm56HTkUxGZBohjLkP5z5slVbvJDwDCkFcTugL97L8vOMi5oEZCs81sNZA5RRRtplKfOnf0hmDHeOFXXBVOZAjeiEhU4ZALqXUAD92qbgYZAuOJ0fslM7CXOyReUnyx6AxwFSLFSv0Qnm6HQZDZD"
    WHATSAPP_APP_SECRET: str = "ece92b43019a49d79f12841675d9a96f"  # used to verify X-Hub-Signature-256
    WHATSAPP_TEMPLATE_NAME: str = "vendor_booking_confirm"
    GRAPH_API_VERSION: str = "v21.0"
    # "template" once vendor_booking_confirm is approved, "interactive" fallback
    # (works only inside the 24h customer-service window) until then.
    WHATSAPP_MODE: str = "interactive"

    # --- Webhook ---
    LOCAL_WEBHOOK_URL: str = "http://127.0.0.1:8000/api/v1/webhook/whatsapp"
    # True only in local dev, so scripts/simulate_reply.py works without a real
    # Meta signature. Must be False (default) anywhere internet-facing.
    WEBHOOK_SKIP_SIGNATURE: bool = False

    # --- Payments service (PHP) ---
    PAYMENTS_BASE_URL: str = "http://127.0.0.1:8081"
    PAYMENTS_SHARED_SECRET: str = "change_me_shared_secret"
    # If the PHP service is unreachable, mark the payment paid with provider
    # "mock" instead of failing the demo outright.
    PAYMENTS_FALLBACK_MOCK: bool = True

    # --- Seed data ---
    # Comma-separated E.164 numbers, e.g. "+2348012345671,+2348012345672,..."
    DEMO_PHONES: str = ""

    # Property alias so settings.WHATSAPP_TOKEN works seamlessly
    @property
    def WHATSAPP_TOKEN(self) -> str:
        return self.WHATSAPP_ACCESS_TOKEN

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def demo_phone_list(self) -> list[str]:
        return [p.strip() for p in self.DEMO_PHONES.split(",") if p.strip()]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
