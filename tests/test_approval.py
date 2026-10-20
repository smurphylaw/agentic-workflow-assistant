import pytest

from mcp_server import database
from mcp_server.approval import propose_update, decide_approval

def test_proposal_does_not_update_database(test_db):
    result = propose_update(999, "in_progress")

    assert result["success"] is True
    assert result["state"] == "pending"
    assert database.get_request_by_id(999)["status"] == "open"

def test_approval_updates_database(test_db):
    proposal = propose_update(999, "in_progress")
    result = decide_approval(proposal["approval_id"], True)

    assert result["success"] is True
    assert database.get_request_by_id(999)["status"] == "in_progress"

def test_rejection_preserves_status(test_db):
    proposal = propose_update(999, "in_progress")
    result = decide_approval(proposal["approval_id"], False)

    assert result["success"] is True
    assert database.get_request_by_id(999)["status"] == "open"

def test_invalid_transition_rejected(test_db):
    result = propose_update(999, "closed")

    assert result["success"] is False
    assert database.get_request_by_id(999)["status"] == "open"

def test_duplicate_approval_rejected(test_db):
    proposal = propose_update(999, "in_progress")
    first = decide_approval(proposal["approval_id"], True)
    second = decide_approval(proposal["approval_id"], True)

    assert first["success"] is True
    assert second["success"] is False
    assert database.get_request_by_id(999)["status"] == "in_progress"