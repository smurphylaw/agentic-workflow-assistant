import logging

from mcp_server.approval import (
    decide_approval,
    initialize_approvals,
)

from mcp_server.database import get_connection

def main():
    initialize_approvals()

    with get_connection() as conn:
         pending = conn.execute("""
            SELECT a.id, a.request_id,
                   a.original_status, a.requested_status,
                   a.expires_at, r.description
            FROM approvals a
            JOIN requests r ON r.id = a.request_id
            WHERE a.state = 'pending'
            ORDER BY a.created_at
        """).fetchall()

    if not pending:
        print("No pending approvals.")
        return

    for approval in pending:
        print("\n--- Pending Approval ---")
        print(f"ID: {approval['id']}")
        print(f"Request: {approval['request_id']}")
        print(f"Description: {approval['description']}")
        print(f"Current: {approval['original_status']}")
        print(f"Proposed: {approval['requested_status']}")
        print(f"Expires: {approval['expires_at']}")

        answer = input("Approve? (yes/no/skip): ").strip().lower()

        if answer not in {"yes", "no"}:
            print("Skipped.")
            continue

        result = decide_approval(
            approval["id"],
            approve=(answer == "yes"),
        )

        print(result)

if __name__ == "__main__":
    main()