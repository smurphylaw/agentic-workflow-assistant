import pytest

from mcp_server import database

@pytest.fixture
def test_db(tmp_path, monkeypatch):
    monkeypatch.setattr(
        database,
        "DB_PATH",
        tmp_path / "test_requests.db"
    )

    database.initialize_database()

    with database.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO requests (id, category, description, status)
            VALUES (?, ?, ?, ?)
            """,
            (999, "access", "Test access issue", "open")
        )

    yield

@pytest.fixture
def anyio_backend():
    return "asyncio"