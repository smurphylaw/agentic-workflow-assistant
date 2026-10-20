import asyncio

from mcp import Client
from mcp_server.server import mcp

def show_result(result):
    print("Is error:", result.is_error)
    print("Structured Content:", result.structured_content)

    for item in result.content:
        if item.type == "text":
            print("Text content:", item.text)

async def main():
    async with Client(mcp) as client:
        result = await client.list_tools()
        tools = result.tools

        print("\nAvailable MCP tools:")
        for tool in tools:
            print(f"  - {tool.name}")

        names = {tool.name for tool in tools}
        
        assert names == {
            "get_request",
            "search_history",
            "update_request_status",
        }

        print("\nTesting get_request...")
        result = await client.call_tool(
            "get_request",
            {"request_id": 104},
        )
        show_result(result)

        print("\nTesting search_history...")
        result = await client.call_tool(
            "search_history",
            {"category": "access"},
        )
        show_result(result)

        print("\nTesting unauthorized update...")
        result = await client.call_tool(
            "update_request_status",
            {"request_id": 104, "status": "resolved"},
        )
        show_result(result)

        print("\nTesting missing request...")
        result = await client.call_tool(
            "get_request",
            {"request_id": 999},
        )
        show_result(result)

        print("\nMCP tests completed.")


if __name__ == "__main__":
    asyncio.run(main())