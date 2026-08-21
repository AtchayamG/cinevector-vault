# 🎥 3-Minute Demo Video Script: CineVector Vault (ClickHouse Track)

**Note: This video demonstrates real live ClickHouse MCP SQL queries against a self-hosted cluster, while using deterministic fixtures for Gemini unless credentials are supplied.**

- **[0:00 - 0:45] The Problem & Architecture**: Introduce visual continuity drift in generative video filmmaking. Explain that this recording executes live ClickHouse queries using the official `mcp-clickhouse` server over stdio, connected to a local self-hosted cluster. Gemini extraction uses local fixture mode for the demo.
- **[0:45 - 1:30] Gemini 2.5 Flash Feature Extraction (Local Fixture)**: Show the web interface (`http://localhost:8001`). Select character Maya Vance. Demonstrate how the app extracts visual tokens (costume, lighting, facial traits) using dynamic local fixtures that simulate the Gemini 2.5 Flash contract.
- **[1:30 - 2:15] Official Live ClickHouse MCP Execution**: Trigger the SQL analytics or vector similarity match. Show the real live MCP SQL query execution against the self-hosted ClickHouse cluster, proving the partner integration. Emphasize that the query result (e.g. Elias Thorn: 1, Maya Vance: 2) is from a genuine runtime execution.
- **[2:15 - 3:00] Reviewing the Code Path**: Walk through the backend architecture (`backend/app/mcp/clickhouse_mcp_server.py`) to show the live code path that manages a stdio session with the official `mcp-clickhouse` server package and Python MCP SDK. Conclude by reiterating that the live SQL and vector search execution is fully active and verified.
