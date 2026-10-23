# Agentic AI Workflow Automation Assistant

A local, agentic AI application built with Google Gemini, Google Agent Development Kit (ADK), Model Context Protocol (MCP), Python, and SQLite.

The assistant investigates operational requests, retrieves relevant historical incidents, recommends next steps, and proposes workflow status changes that require explicit human approval.

## Overview

This project explores how AI agents can interact with operational systems through MCP while maintaining human oversight of state-changing actions.

Unlike a traditional chatbot, the assistant dynamically selects and invokes tools based on the user's request.

### Key Features

- **Agentic investigation:** Gemini dynamically selects MCP tools to investigate operational requests.
- **Historical analysis:** Retrieves previously resolved incidents to support recommendations.
- **MCP integration:** Exposes operational tools through a Python MCP server.
- **Human-in-the-loop approval:** Status changes require explicit human authorization.
- **Workflow validation:** Enforces valid status transitions.
- **Structured logging:** Records MCP tool activity.
- **Automated testing:** Uses pytest to validate core functionality.

## Architecture

```text
                  User
                    |
                    v
            Google ADK Agent
                    |
                    v
                  Gemini
                    |
                    v
               MCP Toolset
                    |
                    v
             Python MCP Server
                    |
          +---------+---------+
          |         |         |
          v         v         v
     get_request  search_   update_request_
                  history      status
          |         |         |
          v         v         v
              SQLite Database
                              |
                              v
                       Pending Approval
                              |
                              v
                       Human Review CLI
                              |
                       +------+------+
                       |             |
                    Approve         Deny
                       |             |
                       v             v
                 Update Status    No Change
```

The agent can investigate requests and propose changes, but it cannot directly authorize database updates.

## Technology Stack

| Component | Technology |
|-----------|------------|
| AI Model | Google Gemini |
| Agent Framework | Google ADK |
| Tool Integration | Model Context Protocol (MCP) |
| Backend | Python |
| Database | SQLite |
| Testing | pytest |
| Configuration | python-dotenv |

## MCP Tools

The MCP server exposes three tools:

### `get_request`

Retrieves an operational request by its ID.

### `search_history`

Searches previously resolved requests within a category to identify relevant historical incidents and resolutions.

### `update_request_status`

Validates a requested status transition and creates a pending approval.

**Important:** This tool does not directly update the request.

## Human-in-the-Loop Approval

Supported request statuses:

```text
open -> in_progress -> resolved -> closed
```

A resolved request can also transition back to `in_progress`.

When Gemini proposes a status change:

1. The MCP server validates the request and transition.
2. A pending approval record is created.
3. The agent reports the approval requirement.
4. A human reviews the proposal using the local CLI.
5. An approved proposal updates the database.
6. A rejected proposal leaves the request unchanged.

Approvals expire after 15 minutes and cannot be reused.

The approval mechanism operates outside the agent's available MCP tools.

## Getting Started

### Prerequisites

- Python 3.13
- Google Gemini API key

### Installation

Clone the repository:

```bash
git clone https://github.com/smurphylaw/agentic-workflow-assistant
cd Agentic-Workflow-Assistant
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Update `.env` with your Google API key.

```env
GOOGLE_API_KEY=your_api_key
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GEMINI_MODEL=gemini-3-flash-preview
```

### Initialize Sample Data

```bash
python -m scripts.seed_db
```

### Launch the Agent

```bash
adk web .
```

Open the local ADK interface and select `workflow_agent`.

## Example Usage

### Investigate an Operational Request

Prompt:

> Investigate operational request 105. Find relevant historical incidents, identify possible causes, and recommend the next steps.

The agent retrieves request 105, searches historical infrastructure incidents, and generates recommendations based on the available evidence.

### Propose a Status Change

Prompt:

> Change request 105 from open to in_progress.

The agent invokes the MCP status-update tool and creates a pending approval.

The request remains unchanged until a human approves it.

### Review Pending Approvals

In a separate terminal:

```bash
python -m scripts.review_approvals
```

Approve or reject the pending proposal.

## Testing

Run the automated test suite:

```bash
python -m pytest tests/ -v
```

The test suite covers:

- Request retrieval
- Historical incident searches
- Missing-request handling
- Status-update proposals
- Approval execution
- Approval rejection
- Invalid transitions
- Duplicate approval prevention
- Verification that proposals do not directly modify request status

## Project Scope

This is a local learning project developed to gain hands-on experience with agentic AI, Google ADK, Gemini, MCP, and human-in-the-loop workflow automation.
