# 🎥 3-Minute Demo Video Script: CineVector Vault (ClickHouse Track)

- **[0:00 - 0:45] The Problem**: Visual continuity drift in generative video filmmaking (characters changing outfits, lighting, or faces across scenes).
- **[0:45 - 1:30] Gemini 2.5 Flash Feature Extraction**: Show the web interface (`http://localhost:8001`), select character Maya Vance, and demonstrate Gemini 2.5 Flash decomposing the shot into structured visual tokens (costume, lighting, facial traits).
- **[1:30 - 2:15] ClickHouse MCP Vector Search**: Trigger vector similarity match. Show the query executed via official `mcp-clickhouse` server over ClickHouse reference tables, showing matched reference frames and cosine similarity score.
- **[2:15 - 3:00] ClickHouse SQL Console & Conclusion**: Run a SQL query on the MergeTree table via official MCP `run_query` tool and summarize the architecture.
