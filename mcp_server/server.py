
import json
import logging
import sys

from mcp.server import MCPServer

from mcp_server.database import (
    get_request_by_id,
    search_requests_by_category,
    change_request_status,
)
from mcp_server.approval import propose_update

# Logging Configuration
# logging.basicConfig(
#     level=logging.INFO,
#     format=(
#         '{"level":"%(levelname)s",'
#         '"logger":%(name)s",'
#         '"message":"%(message)s"'
#         '}'
#     ),
#     stream=sys.stderr
# )

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        })

handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(JSONFormatter())

logger = logging.getLogger("workflow_mcp")
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(handler)
logger.propagate = False

# MCP Server Initialization
mcp = MCPServer("Operational Workflow Assistant")

# MCP Tools
@mcp.tool()
def get_request(request_id: int):
    """Retrieve an operational request by its ID."""
    logger.info("get_request_id=%s", request_id)

    try:
        request = get_request_by_id(request_id)

        if request is None:
            return {
                "success": False,
                "error": f"Request {request_id} not found",
            }

        return {"success": True, "request": request}

    except Exception:
        logger.exception("get_request failed")
        return {
            "success": False,
            "error": "Database operation failed",
        }

@mcp.tool()
def search_history(category: str) -> dict:
    """Find resolved historical requests in a category.

    Use previous resolutions to investigate similar
    operational issues and recommend next steps.
    """

    logger.info("search_history category=%s", category)

    try:
        requests = search_requests_by_category(category)

        return {
            "success": True,
            "category": category,
            "count": len(requests),
            "requests": requests,
        }

    except Exception:
        logger.exception("search_history failed")
        return {
            "success": False,
            "error": "Database operation failed",
        }

@mcp.tool()
def update_request_status(request_id: int, status: str) -> dict:
    """Propose a status update for an operational request.

    This tool does not directly modify the request.
    It creates a pending proposal requiring human approval.

    Tell the user the current status, requested status,
    and that approval is required.
    """

    logger.info(
        "update_requested id=%s status=%s",
        request_id,
        status,
    )

    try:
        return propose_update(request_id, status)

    except Exception:
        logger.exception("Failed to create update proposal")
        return {
            "success": False,
            "error": "Unable to create approval proposal",
        }

# Server entry point
if __name__ == "__main__":
    mcp.run()