from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    APP_ENV: str = "development"
    USE_MOCK_WHATSAPP: bool = True

    # Meta WhatsApp API Credentials
    WHATSAPP_VERIFY_TOKEN: str = "vendly_secret_verify_token"
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""

    # Webhook Callback Settings
    LOCAL_WEBHOOK_URL: str = "http://127.0.0.1:8000/api/v1/webhook/whatsapp"

    # Property alias so settings.WHATSAPP_TOKEN works seamlessly
    @property
    def WHATSAPP_TOKEN(self) -> str:
        return self.WHATSAPP_ACCESS_TOKEN

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()