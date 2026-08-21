import os
import sys
import asyncio

# Ensure the backend directory is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.mcp.clickhouse_mcp_server import clickhouse_mcp_server
from app.config import settings

async def main():
    if not os.environ.get('CLICKHOUSE_HOST') or not os.environ.get('CLICKHOUSE_PASSWORD'):
        print('Error: Required environment variables CLICKHOUSE_HOST and CLICKHOUSE_PASSWORD are missing.')
        print('Please export them before running this script.')
        sys.exit(1)
    
    settings.RUNTIME_MODE = 'live'
    # The client reads settings, so make sure they reflect environment
    settings.CLICKHOUSE_HOST = os.environ.get('CLICKHOUSE_HOST')
    settings.CLICKHOUSE_PORT = int(os.environ.get('CLICKHOUSE_PORT', 8123))
    settings.CLICKHOUSE_USER = os.environ.get('CLICKHOUSE_USER', 'default')
    settings.CLICKHOUSE_PASSWORD = os.environ.get('CLICKHOUSE_PASSWORD')
    settings.CLICKHOUSE_SECURE = os.environ.get('CLICKHOUSE_SECURE', 'false').lower() == 'true'

    query = "SELECT character, count() AS shots FROM video_frames GROUP BY character ORDER BY character"
    print(f"Executing Live MCP Query: {query}")
    
    result = await clickhouse_mcp_server.call_tool("run_query", {"query": query})
    
    if result.get("status") == "error":
        print(f"Query Failed:\n{result.get('error')}")
        sys.exit(1)
        
    print("\n--- Query Result ---")
    print(result.get("mcp_output", "No output returned"))
    print("--------------------\n")
    print(f"Evidence Source: {result.get('evidence_source')}")
    print(f"Project Response Mode: {result.get('mode')}")

if __name__ == "__main__":
    asyncio.run(main())
