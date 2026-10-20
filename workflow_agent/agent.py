import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StdioConnectionParams,
)
from mcp import StdioServerParameters

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

root_agent = Agent(
    name="workflow_assistant",
    model=os.getenv("GEMINI_MODEL", "gemini-3-flash-preview"),
    description="AI assistant for investigating operational requests.",
    instruction="""
    You are an operational workflow assistant.

    Your responsibilites:
    1. Investigate operational requests using available MCP tools.
    2. Retrieve request details when investigating a specific request.
    3. Search relevant historical requests when useful.
    4. Compare historical resolutions and recommend practical next steps.
    5. Clearly distinguish known facts from hypotheses.
    6. Never claim that a request status was updated unless the tool confirms it.
    7. When a status change is requested, use the update_request_status tool to create an approval proposal.
    8. Explain that a human must approve the proposal before the database status changes.

    Do not invent request records, historical resolutions, or tool results.

    VALID REQUEST STATUSES:
    - open
    - in_progress
    - resolved
    - closed

    ALLOWED STATUS TRANSITIONS:
    - open -> in_progress
    - in_progress -> resolved
    - resolved -> closed
    - resolved -> in_progress

    STATUS UPDATE RULES:
    - Do not propose a status change unless the user explicitly requests one.
    - Never invent status values such as "investigating".
    - When a user requests a status change, call update_request_status.
    - A successful tool response creates a pending approval, not a completed update.
    - Only claim that a proposal was created when the tool returns success=true and state=pending.
    - If the tool returns success=false, explain the error.
    - Never claim that a database status changed unless a trusted tool confirms it.
    """,
    tools =[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=sys.executable,
                    args=["-m", "mcp_server.server"],
                    cwd=str(PROJECT_ROOT),
                ),
                timeout=30,
            ),
        ),
    ]
)