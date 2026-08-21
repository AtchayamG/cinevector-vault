import os
import sys
import shutil
import logging
from typing import Dict, Any, List
from app.config import settings
from app.services.clickhouse_service import clickhouse_service

logger = logging.getLogger("cinevector.mcp")

# Official tool schemas exposed by mcp-clickhouse
OFFICIAL_MCP_TOOLS = [
    {
        "name": "run_query",
        "description": "Execute SQL queries in ClickHouse via official mcp-clickhouse server.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "SQL query to execute"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "list_databases",
        "description": "List available ClickHouse databases.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "list_tables",
        "description": "List available ClickHouse tables in a database.",
        "parameters": {
            "type": "object",
            "properties": {
                "database": {"type": "string", "description": "Database name"}
            },
            "required": ["database"]
        }
    }
]

class ClickHouseMCPClient:
    """
    Official MCP Client Path for mcp-clickhouse.
    Manages stdio MCP sessions with the installed official `mcp-clickhouse` server process.
    Uses official Python `mcp` SDK (StdioServerParameters, stdio_client, ClientSession).
    """
    def __init__(self):
        self.server_name = "mcp-clickhouse"

    def list_tools(self) -> List[Dict[str, Any]]:
        return OFFICIAL_MCP_TOOLS

    async def _execute_live_mcp_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Connects to official mcp-clickhouse server via stdio transport using official MCP SDK
        and invokes the requested tool.
        Returns live_unavailable / live_error on failure without falling back to demo success.
        """
        if not settings.CLICKHOUSE_PASSWORD or settings.CLICKHOUSE_HOST in ("", "localhost"):
            return {
                "status": "error",
                "mode": "live_unavailable",
                "error": "Live ClickHouse Cloud credentials (CLICKHOUSE_HOST, CLICKHOUSE_PASSWORD) not configured in .env",
                "evidence_source": "mcp-clickhouse (Live Stdio Session Unconfigured)"
            }

        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client

            env = os.environ.copy()
            env["CLICKHOUSE_HOST"] = settings.CLICKHOUSE_HOST
            env["CLICKHOUSE_PORT"] = str(settings.CLICKHOUSE_PORT)
            env["CLICKHOUSE_USER"] = settings.CLICKHOUSE_USER
            env["CLICKHOUSE_PASSWORD"] = settings.CLICKHOUSE_PASSWORD
            env["CLICKHOUSE_DATABASE"] = settings.CLICKHOUSE_DATABASE
            env["CLICKHOUSE_SECURE"] = "true" if settings.CLICKHOUSE_SECURE else "false"

            cmd = shutil.which("mcp-clickhouse") or sys.executable
            args = [] if shutil.which("mcp-clickhouse") else ["-m", "mcp_clickhouse.main"]

            server_params = StdioServerParameters(
                command=cmd,
                args=args,
                env=env
            )

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    res = await session.call_tool(tool_name, arguments)
                    
                    if getattr(res, "isError", False):
                        err_msg = "".join([c.text for c in getattr(res, "content", []) if hasattr(c, "text")])
                        return {
                            "status": "error",
                            "mode": "live_error",
                            "error": f"Official mcp-clickhouse tool error: {err_msg}",
                            "evidence_source": "mcp-clickhouse (Live Session Error)"
                        }
                    
                    content_str = "".join([c.text for c in getattr(res, "content", []) if hasattr(c, "text")])
                    return {
                        "status": "success",
                        "mode": "live",
                        "evidence_source": "mcp-clickhouse (Official Live MCP Stdio Session)",
                        "tool": tool_name,
                        "mcp_output": content_str
                    }
        except Exception as e:
            logger.error(f"Live mcp-clickhouse stdio call failed: {e}")
            return {
                "status": "error",
                "mode": "live_error",
                "error": f"Official mcp-clickhouse stdio session failed: {str(e)}",
                "evidence_source": "mcp-clickhouse (Live Session Exception)"
            }

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Official ClickHouse MCP Tool Request: {tool_name} with {arguments}")
        
        if settings.RUNTIME_MODE == "live":
            return await self._execute_live_mcp_call(tool_name, arguments)

        # Demo Mode
        if tool_name == "run_query":
            sql = arguments.get("query", "SELECT 1")
            return clickhouse_service.execute_sql(sql)
        elif tool_name == "list_databases":
            return {
                "status": "success",
                "mode": "demo",
                "evidence_source": "ClickHouse MergeTree (Local Fixture)",
                "databases": ["default", "cinevector_vault", "system"]
            }
        elif tool_name == "list_tables":
            return {
                "status": "success",
                "mode": "demo",
                "evidence_source": "ClickHouse MergeTree (Local Fixture)",
                "database": arguments.get("database", "cinevector_vault"),
                "tables": ["video_frames", "script_dialogues", "scene_takes"]
            }
        elif tool_name == "clickhouse_search_vector_continuity":
            return clickhouse_service.search_vector_continuity(
                character=arguments.get("character", "Maya Vance"),
                query_tokens=arguments.get("query_tokens")
            )
        elif tool_name == "clickhouse_execute_sql":
            return clickhouse_service.execute_sql(arguments.get("sql", "SELECT 1"))
        
        return {
            "status": "error",
            "mode": "demo" if settings.RUNTIME_MODE != "live" else "live_error",
            "error": f"Tool '{tool_name}' unknown to mcp-clickhouse"
        }

clickhouse_mcp_server = ClickHouseMCPClient()
