import os
import sqlite3
import hashlib
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("reddit_db")

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database",
    "reddit_commander.db"
)


def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Connect to SQLite database with WAL mode and high busy timeout."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initialize the schema for the Reddit Watcher and Ledger."""
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reddit_watchlist (
                    subreddit TEXT PRIMARY KEY,
                    last_scraped_utc REAL,
                    after_cursor TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reddit_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT (datetime('now', 'utc')),
                    action TEXT,
                    subreddit TEXT,
                    target_id TEXT,
                    content_hash TEXT UNIQUE,
                    status TEXT,
                    reddit_url TEXT,
                    approval_ref TEXT
                )
            """)
        logger.info(f"Database initialized successfully at {db_path}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    finally:
        conn.close()


def get_watchlist(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Retrieve all watched subreddits."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT subreddit, last_scraped_utc, after_cursor FROM reddit_watchlist")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def update_watchlist(subreddit: str, last_scraped_utc: float, after_cursor: str, db_path: str = DEFAULT_DB_PATH) -> None:
    """Upsert the scraping cursor information for a subreddit."""
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute("""
                INSERT INTO reddit_watchlist (subreddit, last_scraped_utc, after_cursor)
                VALUES (?, ?, ?)
                ON CONFLICT(subreddit) DO UPDATE SET
                    last_scraped_utc = excluded.last_scraped_utc,
                    after_cursor = excluded.after_cursor
            """, (subreddit, last_scraped_utc, after_cursor))
        logger.info(f"Updated watchlist cursor for r/{subreddit}: after={after_cursor}")
    finally:
        conn.close()


def compute_content_hash(text: str) -> str:
    """Compute deterministic SHA-256 hash of text content."""
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def check_duplicate_content(content_hash: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Check if content has already been posted to prevent duplication."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM reddit_ledger WHERE content_hash = ? LIMIT 1", (content_hash,))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def add_ledger_entry(
    action: str,
    subreddit: str,
    target_id: str,
    content_hash: str,
    status: str,
    reddit_url: str,
    approval_ref: str,
    db_path: str = DEFAULT_DB_PATH
) -> None:
    """Insert an entry into the immutable ledger."""
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute("""
                INSERT INTO reddit_ledger (action, subreddit, target_id, content_hash, status, reddit_url, approval_ref)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (action, subreddit, target_id, content_hash, status, reddit_url, approval_ref))
        logger.info(f"Added ledger entry: action={action}, sub={subreddit}, status={status}")
    finally:
        conn.close()


def get_ledger(limit: int = 100, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Retrieve recent ledger entries."""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, action, subreddit, target_id, content_hash, status, reddit_url, approval_ref
            FROM reddit_ledger
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
