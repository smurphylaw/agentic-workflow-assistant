import json

import pytest

from mcp import Client

from mcp_server.server import mcp
from mcp_server import database

def parse_result(result):
    assert result.is_error is False

    text = result.content[0].text
    return json.loads(text)

@pytest.mark.anyio
async def test_get_request(test_db):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_request",
            {"request_id": 999},
        )

    data = parse_result(result)

    assert data["success"] is True
    assert data["request"]["id"] == 999
    assert data["request"]["status"] == "open"

@pytest.mark.anyio
async def test_search_history(test_db):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "search_history",
            {"category": "access"},
        )

    data = parse_result(result)

    assert data["success"] is True
    assert data["category"] == "access"

@pytest.mark.anyio
async def test_update_creates_proposal_only(test_db):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "update_request_status",
            {
                "request_id": 999,
                "status": "in_progress",
            },
        )

    data = parse_result(result)

    assert data["success"] is True
    assert data["state"] == "pending"
    assert "approval_id" in data

    # MCP cannot directly change the request status.
    assert database.get_request_by_id(999)["status"] == "open"

@pytest.mark.anyio
async def test_missing_request(test_db):
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_request",
            {"request_id": 123456},
        )

    data = parse_result(result)

    assert data["success"] is False
    assert "not found" in data["error"].lower()