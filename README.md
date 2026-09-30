# Vendly

Vendly is a FastAPI backend for managing events and vendors, with WhatsApp Cloud API integration for vendor notifications and interactive responses.

## Project Status

The backend currently provides:

- A FastAPI application with automatic interactive API documentation.
- SQLite persistence through SQLAlchemy.
- WhatsApp webhook verification and webhook receipt handling.
- Mock and Meta Cloud API WhatsApp clients behind one service interface.
- Event and vendor ORM models and request/response schemas.

The notification router is implemented in `vendly-backend/app/routers/notify.py` and is included in the FastAPI app startup through `app/main.py`, so the send flow is available when the service is running.

## Project Structure

```text
Vendly/
|-- .env                         # Local secrets and settings; do not commit
|-- README.md
|-- .venv                       # Local Python virtual environment (not committed)
`-- vendly-backend/
    |-- requirements.txt
    |-- vendly.db                # Local SQLite database created at runtime
    `-- app/
        |-- config.py            # Environment-backed settings and app defaults
        |-- database.py          # SQLAlchemy engine, session factory, startup DB init
        |-- errors.py            # Shared AppError / validation response handlers
        |-- main.py              # FastAPI app, CORS, router registration, startup hooks
        |-- models.py            # SQLAlchemy ORM models for events, vendors, payments, messages, logs
        |-- schemas.py           # Pydantic request and response validation for events and budgets
        |-- seed.py              # Demo seed data used when the database is empty
        |-- routers/
        |   |-- budget.py        # Budget + payment disbursement endpoints
        |   |-- events.py        # Event create/list/detail/status endpoints
        |   |-- health.py        # Health and dependency checks
        |   |-- notify.py        # Manual notification dispatch route
        |   |-- vendors.py       # Add/edit/delete vendor routes
        |   `-- webhook.py       # WhatsApp webhook verification and reply handling
        `-- services/
            |-- activity.py      # Activity logging helpers for dashboard updates
            |-- payments_client.py  # PHP payments compatibility client and fallback logic
            |-- status.py        # Version bump logic for real-time polling
            `-- whatsapp.py      # Mock and Meta WhatsApp clients + payload builder
```

## Recent project updates

The project has evolved beyond the original notification-only prototype. The backend now includes a more complete event workflow, vendor lifecycle management, webhook-based confirmation flows, and budget/payment handling.

### Current capabilities

- Event creation from a single payload that includes nested vendor data.
- Vendor add/edit/delete operations with validation and conflict handling.
- WhatsApp message sending for pending or failed vendors, with `YES` / `NO` quick-reply logic.
- Webhook verification and reply processing for Meta WhatsApp Cloud API callbacks.
- Payment workflow for deposits and balances with a mock fallback when the external payments service is unavailable.
- Activity tracking and event version bumping to support lightweight polling for dashboard updates.
- Shared error serialization with consistent JSON error responses.
- Automatic startup seeding so local demo data is created when the database is empty.

### Data and business logic notes

- The database uses SQLAlchemy models with SQLite in local development and a configurable `DATABASE_URL` for deployment environments.
- Amounts are stored as integers in minor units (kobo), matching the project’s payment and budget rules.
- Vendor and event statuses follow a finite set of values used by the API and dashboard logic.
- Webhook receipt is intentionally tolerant: the request is acknowledged quickly, recorded, and parsed safely without crashing the app.
- Dashboard polling is optimized through `events.version`, so clients can check whether anything changed rather than refetching the entire event state.

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
USE_MOCK_WHATSAPP=false
WHATSAPP_VERIFY_TOKEN=V3ndly_Wh4t5App_7ok3n_9fK2mQx8
WHATSAPP_PHONE_NUMBER_ID=1426941730493435
WHATSAPP_ACCESS_TOKEN=EAANkxqqBgOQBSi2pJiaAnGSKbSLkoAfjuJhuHDLZBEfdbvCZAZBnm56HTkUxGZBohjLkP5z5slVbvJDwDCkFcTugL97L8vOMi5oEZCs81sNZA5RRRtplKfOnf0hmDHeOFXXBVOZAjeiEhU4ZALqXUAD92qbgYZAuOJ0fslM7CXOyReUnyx6AxwFSLFSv0Qnm6HQZDZD
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

The current WhatsApp flow uses quick-reply payloads in the form `YES:{vendor_id}` and `NO:{vendor_id}`. The webhook parser confirms the vendor and updates status based on the response.

## Data Model

The SQLite database contains the following core tables:

- `events`: event metadata, schedule, venue, notes, status, version, and timestamps.
- `vendors`: vendor contact details, event relationship, role, phone number, status, deposit, and balance amounts.
- `messages`: outbound and inbound WhatsApp message records, payloads, and delivery status.
- `payments`: deposit and balance payment records, provider metadata, and payment state.
- `activity`: event activity feed for dashboard updates and auditing.
- `webhook_events`: raw webhook payloads and processing state for debugging and idempotency.

Vendor statuses default to `pending`, with transitions such as `sent`, `confirmed`, `declined`, and `failed`.

## Development Notes

- The application creates database tables automatically through SQLAlchemy on startup.
- There are no migration files yet; schema changes should be handled carefully before deploying to a shared database.
- The notification route definition in `app/routers/notify.py` expects `WhatsAppClient` dependency injection. Register it in `app/main.py` when exposing the notification API:

```python
from app.routers.notify import router as notify_router

app.include_router(notify_router)
```

- Do not commit `.env`, access tokens, local database files, or Python cache directories.

## API overview

The current backend exposes the following main routes:

```text
GET  /                                     # API status
GET  /api/v1/health                        # health + dependency status
POST /api/v1/events                        # create event + vendors
GET  /api/v1/events                        # list events
GET  /api/v1/events/{event_id}            # event details
GET  /api/v1/events/{event_id}/status     # lightweight poll status response
POST /api/v1/events/{event_id}/vendors     # add one or many vendors
PATCH /api/v1/events/{event_id}/vendors/{vendor_id}
DELETE /api/v1/events/{event_id}/vendors/{vendor_id}
POST /api/v1/notify/send                   # send confirmation messages
GET  /api/v1/webhook/whatsapp             # Meta verification endpoint
POST /api/v1/webhook/whatsapp             # webhook event receiver
GET  /api/v1/events/{event_id}/budget     # budget + payment status
POST /api/v1/budget/{vendor_id}/disburse  # deposit / balance disbursement
```

## Folder and environment guidance

- The root project folder contains the local runtime environment file and the main app workspace.
- `vendly-backend/app` is the actual FastAPI application package.
- The `app/services` layer isolates third-party integrations such as WhatsApp and payment processing.
- `app/routers` contains the public API contract and keeps route logic separate from database and business rules.
- `.env` should remain local to your machine and never be checked into source control.
- If you deploy the app to a hosted environment, provide secrets via environment variables or the platform’s secret manager instead of committing them to the repository.

## License

No license has been specified for this project yet.
