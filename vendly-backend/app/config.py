from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    APP_ENV: str = "development"
    USE_MOCK_WHATSAPP: bool = True

    # Meta WhatsApp API Credentials
    WHATSAPP_VERIFY_TOKEN: str = "V3ndly_Wh4t5App_7ok3n_9fK2mQx8"
    WHATSAPP_PHONE_NUMBER_ID: str = "1426941730493435"
    WHATSAPP_ACCESS_TOKEN: str = "EAANkxqqBgOQBSi2pJiaAnGSKbSLkoAfjuJhuHDLZBEfdbvCZAZBnm56HTkUxGZBohjLkP5z5slVbvJDwDCkFcTugL97L8vOMi5oEZCs81sNZA5RRRtplKfOnf0hmDHeOFXXBVOZAjeiEhU4ZALqXUAD92qbgYZAuOJ0fslM7CXOyReUnyx6AxwFSLFSv0Qnm6HQZDZD"

    # Webhook Callback Settings
    LOCAL_WEBHOOK_URL: str = "http://127.0.0.1:8000/api/v1/webhook/whatsapp"

    # Property alias so settings.WHATSAPP_TOKEN works seamlessly
    @property
    def WHATSAPP_TOKEN(self) -> str:
        return self.WHATSAPP_ACCESS_TOKEN

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()