#!/usr/bin/env python3
# db_connector.py — Centralized SQLite database connector for Tesla memory management.
# Restricts empty database creations under Sandboxes using mode=rw.

import os
import sqlite3

# Dynamically resolve the workspace root (one level up from the current script directory)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WORKSPACE = os.path.dirname(CURRENT_DIR)

WORKSPACE = DEFAULT_WORKSPACE

DB_PATH = os.environ.get(
    "ALEXANDRIA_DB_PATH",
    os.path.abspath(os.path.join(WORKSPACE, "Avalon/03-Resources/alexandria_brain.db"))
)

def get_db_connection(create_if_missing=False):
    """
    Returns an SQLite connection to the Alexandria Brain database.
    Enforces WAL mode, foreign keys, and a high busy timeout.
    If create_if_missing is False (default), it enforces mode=rw to avoid
    silently creating a new empty database file.
    """
    if not create_if_missing and not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Database file not found at: {DB_PATH}. "
            "Operational scripts must not run without a pre-existing database."
        )
    
    # SQLite connection URI
    if create_if_missing:
        # Standard connection allowed to create files if missing (for initialization)
        db_uri = f"file:{DB_PATH}"
    else:
        # Read-Write only, fails if the database file does not exist
        db_uri = f"file:{DB_PATH}?mode=rw"
        
    conn = sqlite3.connect(db_uri, uri=True)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 10000;")
    return conn
