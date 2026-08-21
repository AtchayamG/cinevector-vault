# 🎥 3-Minute Demo Video Script: CineVector Vault (ClickHouse Track)

**Note: This video explicitly demonstrates the app in Demo Mode, using local deterministic fixtures while highlighting the official live code path.**

- **[0:00 - 0:45] The Problem & Demo Mode Disclaimer**: Introduce visual continuity drift in generative video filmmaking. Explain that this recording uses "Demo Mode" with dynamic local visual-token fixtures and deterministic continuity scoring, as live ClickHouse execution proof is blocked until live credentials or a self-hosted cluster are connected.
- **[0:45 - 1:30] Gemini 2.5 Flash Feature Extraction (Local Fixture)**: Show the web interface (`http://localhost:8001`). Select character Maya Vance. Demonstrate how the app extracts visual tokens (costume, lighting, facial traits) using dynamic local fixtures that simulate the Gemini 2.5 Flash contract.
- **[1:30 - 2:15] Deterministic Vector Continuity Scoring**: Trigger the vector similarity match. Show the deterministic continuity scoring and simulated results returned from our local reference fixtures, clearly identifying them as simulated rather than live.
- **[2:15 - 3:00] Official Live Code Path & Architecture**: Walk through the backend architecture (`backend/app/mcp/clickhouse_mcp_server.py`) to show the official live code path that manages a stdio session with the official `mcp-clickhouse` server package and Python MCP SDK. Conclude by reiterating that the live SQL and vector search execution only activates when credentials are provided.
