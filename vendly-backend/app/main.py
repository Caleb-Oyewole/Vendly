"""
Wires everything together: CORS, error handlers, all six routers, DB init,
and the demo seed. Previously the webhook GET/POST handlers lived directly
in this file with no signature check and no status-updating logic -- both
have moved into routers/webhook.py and now actually work end to end.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.errors import install_error_handlers
from app.routers import events, vendors, notify, webhook, budget, health
from app import seed

init_db()
seed.run_if_empty()

app = FastAPI(
    title="Vendly API",
    version=settings.APP_VERSION,
    description="Backend service for event vendor management and WhatsApp automated notifications",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

install_error_handlers(app)

app.include_router(events.router)
app.include_router(vendors.router)
app.include_router(notify.router)
app.include_router(webhook.router)
app.include_router(budget.router)
app.include_router(health.router)


@app.get("/", tags=["Default"])
def read_root():
    return {"message": "Vendly API is active"}
