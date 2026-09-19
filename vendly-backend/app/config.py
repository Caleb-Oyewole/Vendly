import os

# Meta WhatsApp Cloud API Credentials (retrieve from Meta Developer Dashboard)
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "YOUR_TEMPORARY_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "YOUR_PHONE_NUMBER_ID")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "vendly_secret_verify_token")