from mcp_server.database import (
    get_connection,
    initialize_database,
)

SEED_REQUESTS = [
    (
        101,
        "access",
        "New employee cannot access internal reporting portal",
        "resolved",
        "Assigned missing reporting role and verified access",
    ),
    (
        102,
        "access",
        "User receives permission denied error",
        "closed",
        "Corrected IAM group membership",
    ),
    (
        103,
        "infrastructure",
        "Application response times increased after deployment",
        "resolved",
        "Rolled back deployment and corrected connection pool",
    ),
    (
        104,
        "access",
        "Finance employee cannot access reporting dashboard",
        "open",
        None,
    ),
    (
        105,
        "infrastructure",
        "Service intermittently returns HTTP 503",
        "open",
        None,
    ),
    (
        106,
        "billing",
        "Customer reports duplicate invoice",
        "resolved",
        "Identified duplicate processing and issued credit",
    ),
    (
        107,
        "billing",
        "Customer reports incorrect invoice amount",
        "open",
        None,
    ),
]

def main():
    initialize_database()

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO requests
            (id, category, description, status, resolution)
            VALUES (?, ?, ?, ?, ?)
            """,
            SEED_REQUESTS,
        )

    print(f"Seeded {len(SEED_REQUESTS)} requests.")

if __name__ == "__main__":
    main()