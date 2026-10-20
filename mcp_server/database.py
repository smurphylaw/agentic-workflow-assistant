import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "request.db"

VALID_STATUSES = {
    "open",
    "in_progress",
    "resolved",
    "closed",
}

ALLOWED_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": {"closed", "in_progress"},
    "closed": set(),
}

@contextmanager
def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()
    except Exception: 
        conn.rollback()
        raise
    finally:
        conn.close()

def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL, 
                resolution TEXT
            )
        """)

def get_request_by_id(request_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM requests WHERE id = ?",
            (request_id,),
        ).fetchone()

        return dict(row) if row else None

def search_requests_by_category(category: str):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM requests
            WHERE LOWER(category) = LOWER(?)
            AND resolution IS NOT NULL
            ORDER BY id
            """,
        (category,),
        ).fetchall()

        return [dict(row) for row in rows]

def change_request_status(request_id: int, new_status: str):
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {new_status}")

    with get_connection() as conn:
        row = conn.execute(
            "SELECT status from requests WHERE id = ?",
            (request_id,),
        ).fetchone()

        if row is None:
            raise ValueError(f"Request not found: {request_id}")

        current_status = row["status"]

        if new_status not in ALLOWED_TRANSITIONS[current_status]:
            raise ValueError(
                f"Transition not allowed: "
                f"{current_status} -> {new_status}"
            )

        conn.execute(
            "UPDATE requests SET status = ? WHERE id = ?",
            (new_status, request_id),
        )

    return {
        "request_id": request_id,
        "previous_status": current_status,
        "new_status": new_status,
    }