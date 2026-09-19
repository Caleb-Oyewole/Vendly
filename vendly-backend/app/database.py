# app/database.py
import sqlite3

DB_NAME = "vendly.db"


def get_db():
    """
    FastAPI dependency that yields a database connection per request.
    Enables dictionary-like row attribute access across all routers.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Enables dict-style column access (e.g., row["title"])
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """
    Initializes SQLite tables on server startup if they do not already exist.
    Creates both 'events' and 'vendors' tables with primary and foreign key constraints.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Create Events Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            organizer_name TEXT NOT NULL
        )
        """
    )

    # 2. Create Vendors Table linked to Events
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            deposit_amount REAL DEFAULT 0.0,
            balance_amount REAL DEFAULT 0.0,
            status TEXT DEFAULT 'PENDING',
            FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE
        )
        """
    )

    conn.commit()
    conn.close()