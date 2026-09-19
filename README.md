# Vendly

Vendly is a FastAPI backend for managing events and vendors, with WhatsApp Cloud API integration for vendor notifications and interactive responses.

## Project Status

The backend currently provides:

- A FastAPI application with automatic interactive API documentation.
- SQLite persistence through SQLAlchemy.
- WhatsApp webhook verification and webhook receipt handling.
- Mock and Meta Cloud API WhatsApp clients behind one service interface.
- Event and vendor ORM models and request/response schemas.

The notification router is implemented in `vendly-backend/app/routers/notify.py`, but it is not yet registered in `app/main.py`. The endpoint becomes available after including that router in the FastAPI application.

## Project Structure

```text
Vendly/
|-- .env                         # Local secrets and settings; do not commit
|-- README.md
`-- vendly-backend/
    |-- requirements.txt
    |-- vendly.db                # Local SQLite database created at runtime
    `-- app/
        |-- config.py            # Environment-backed settings
        |-- database.py          # SQLAlchemy engine and session dependency
        |-- main.py              # FastAPI application and live routes
        |-- models.py             # Event and Vendor database models
        |-- schemas.py            # Pydantic request and response schemas
        |-- routers/
        |   `-- notify.py        # Notification route definition
        `-- services/
            `-- whatsapp.py      # Mock and Meta WhatsApp clients
```

## Requirements

- Python 3.13 or a compatible recent Python version
- `pip`
- A virtual environment
- Meta WhatsApp Cloud API credentials only when mock mode is disabled

## Setup

From the repository root on Windows:

```powershell
cd vendly-backend
py -3.13 -m venv ..\.venv
..\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a `.env` file in the repository root. The application loads this file through Pydantic Settings:

```env
APP_ENV=development
USE_MOCK_WHATSAPP=true
WHATSAPP_VERIFY_TOKEN=vendly_secret_verify_token
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_ACCESS_TOKEN=
LOCAL_WEBHOOK_URL=http://127.0.0.1:8000/api/v1/webhook/whatsapp
```

Keep `.env` out of source control. In production, provide secrets through the hosting platform's environment configuration instead.

## Run Locally

From `vendly-backend` with the virtual environment active:

```powershell
uvicorn app.main:app --reload
```

The API is available at:

- `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

The SQLite database is created as `vendly-backend/vendly.db` when the application starts.

## Live API Endpoints

### Health and root

```http
GET /
```

Returns a simple application status message.

### Verify the WhatsApp webhook

```http
GET /api/v1/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=<token>&hub.challenge=<challenge>
```

Meta calls this endpoint during webhook setup. The supplied token must match `WHATSAPP_VERIFY_TOKEN`.

### Receive WhatsApp webhook events

```http
POST /api/v1/webhook/whatsapp
Content-Type: application/json
```

The endpoint accepts WhatsApp webhook payloads and logs interactive button reply IDs. It returns a success response for valid payload structures.

## WhatsApp Configuration

`USE_MOCK_WHATSAPP` controls the client selected by `get_whatsapp_client()`:

- `true`: uses `MockWhatsAppClient`, logs the outgoing notification, and attempts to send a simulated webhook to `LOCAL_WEBHOOK_URL`.
- `false`: uses `MetaWhatsAppClient` and sends an interactive button message through the Meta Graph API.

For Meta mode, set:

```env
USE_MOCK_WHATSAPP=false
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_VERIFY_TOKEN=your_webhook_verify_token
```

The Meta client sends `Accept` and `Decline` buttons with reply IDs in the form `ACCEPTED_<vendor_id>` and `DECLINED_<vendor_id>`.

## Data Model

The SQLite database contains:

- `events`: event title and organizer name.
- `vendors`: vendor contact details, event relationship, status, deposit, and balance amounts.

Vendor statuses default to `PENDING`.

## Development Notes

- The application creates database tables automatically through SQLAlchemy on startup.
- There are no migration files yet; schema changes should be handled carefully before deploying to a shared database.
- The notification route definition in `app/routers/notify.py` expects `WhatsAppClient` dependency injection. Register it in `app/main.py` when exposing the notification API:

```python
from app.routers.notify import router as notify_router

app.include_router(notify_router)
```

- Do not commit `.env`, access tokens, local database files, or Python cache directories.

## License

No license has been specified for this project yet.
