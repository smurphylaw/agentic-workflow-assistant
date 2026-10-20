import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

from mcp_server.database import (
    DB_PATH,
    ALLOWED_TRANSITIONS,
    get_connection,
)

APPROVAL_MINUTES = 15

def initialize_approvals():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS approvals (
                id TEXT PRIMARY KEY,
                request_id INTEGER NOT NULL,
                requested_status TEXT NOT NULL,
                originaL_status TEXT NOT NULL,
                state TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
        """
    )

def propose_update(request_id: int, status: str) -> dict:
    initialize_approvals()

    with get_connection() as conn:
        row = conn.execute(
            "SELECT status FROM requests WHERE id = ?",
            (request_id,),
        ).fetchone()

        if row is None:
            return {
                "success": False,
                "error": f"Request {request_id} not found",
            }

        current = row["status"]

        if status not in ALLOWED_TRANSITIONS.get(current, set()):
            return {
                "success": False,
                "error": f"Invalid transition: {current} -> {status}"
            }

        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=APPROVAL_MINUTES)
        approval_id = secrets.token_hex(8)

        conn.execute(
            """
            INSERT INTO approvals
            (id, request_id, requested_status,
             original_status, state, created_at, expires_at)
            VALUES (?, ?, ?, ?, 'pending', ?, ?)
            """, (
            approval_id,
            request_id,
            status,
            current,
            now.isoformat(),
            expires.isoformat(),
            )
        )

        return {
            "success": True,
            "state": "pending",
            "approval_id": approval_id,
            "request_id": request_id,
            "current_status": current,
            "requested_status": status,
            "messages": "Human approval required. No update performed."
        }

def decide_approval(approval_id: str, approve: bool) -> dict:
    initialize_approvals()

    with get_connection() as conn:
        # Acquire a write lock before checking and consuming approval.
        conn.execute("BEGIN IMMEDIATE")

        approval = conn.execute(
            "SELECT * FROM approvals WHERE id = ?",
            (approval_id,),
        ).fetchone()

        if approval is None:
            return {"success": False, "error": "Approval not found"}

        if approval["state"] != "pending":
            return {
                "success": False,
                "error": "Approval already processed",
            }

        now = datetime.now(timezone.utc)
        if now >= datetime.fromisoformat(approval["expires_at"]):
            conn.execute(
                "UPDATE approvals SET state = 'expired' WHERE id = ?",
                (approval_id,),
            )
            return {"success": False, "error": "Approval expired"}

        if not approve:
            conn.execute(
                "UPDATE approvals SET state = 'denied' WHERE id = ?",
                (approval_id,),
            )
            return {
                "success": True,
                "state": "denied",
                "message": "No database status change performed",
            }

        request = conn.execute(
            "SELECT status FROM requests WHERE id = ?",
            (approval["request_id"],),
        ).fetchone()

        if request is None:
            return {
                "success": False,
                "error": "Request no longer exists",
            }

        current = request["status"]
        target = approval["requested_status"]

        if (
            current != approval["original_status"]
            or target not in ALLOWED_TRANSITIONS.get(current, set())
        ):
            conn.execute(
                "UPDATE approvals SET state = 'invalidated' WHERE id = ?",
                (approval_id,),
            )
            return {
                "success": False,
                "error": "Request changed or transition is no longer valid",
            }

        conn.execute(
            "UPDATE requests SET status = ? WHERE id = ?",
            (target, approval["request_id"]),
        )
        conn.execute(
            "UPDATE approvals SET state = 'approved' WHERE id = ?",
            (approval_id,),
        )

        return {
            "success": True,
            "state": "approved",
            "request_id": approval["request_id"],
            "previous_status": current,
            "new_status": target,
        }
