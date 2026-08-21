# 📋 Submission Evidence Matrix: Track 2 (ClickHouse Track)

| Official Requirement | Implementation / Evidence Path | Status | Verification Command | Truthful Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Active Runtime Gemini 2.5 Flash Usage** | `backend/app/services/gemini_service.py`<br/>`backend/app/agents/continuity_agent.py` | **PASS** | `pytest tests/test_clickhouse_vault.py` | Calls `google-genai` SDK with `gemini-2.5-flash` for visual feature extraction from scene descriptions. |
| **Official ClickHouse MCP Integration Code Path** | `backend/app/mcp/clickhouse_mcp_server.py`<br/>`backend/app/services/clickhouse_service.py` | **PASS** (Implementation via Python MCP SDK & stdio `mcp-clickhouse` session) | `pytest tests/test_clickhouse_vault.py` | Uses official Python `mcp` SDK to manage stdio session with `mcp-clickhouse` and call official tools (`run_query`, `list_databases`, `list_tables`). |
| **Live Cluster Proof** | Live authenticated connection to ClickHouse Cloud cluster | **BLOCKED** | Authenticated live smoke call | Official MCP implementation is fully in place, but live cluster proof remains BLOCKED until authenticated live credentials (`CLICKHOUSE_HOST` & `CLICKHOUSE_PASSWORD`) are configured and recorded. |
| **Judge-Friendly Web UI** | `backend/app/static/index.html`<br/>`backend/app/main.py` | **PASS** | Open `http://localhost:8001/` | Interactive web studio with Shot Ingestion, Gemini Extraction Inspector, ClickHouse Vector Matcher, and SQL Console. Uses local CSS (no Tailwind CDN) and embedded favicon. |
| **Explicit Live / Demo Mode** | `backend/app/config.py`<br/>`backend/app/services/clickhouse_service.py` | **PASS** | `pytest tests/test_clickhouse_vault.py` | Clear `MODE: DEMO` badge and honest evidence source tags. In live mode, missing configuration or query failure returns `live_unavailable`/`live_error` without silent demo fallback. |
| **Small Reproducible Seed Dataset** | `backend/app/services/clickhouse_service.py` | **PASS** | File inspect | 3 reference shots with 768-dim embeddings across Maya Vance and Dr. Chen. Demo matching uses dynamic input-dependent vector scoring. |
| **Open Source License** | `LICENSE` | **PASS** | File inspect | Apache 2.0 Open Source License. |
| **Environment Template** | `.env.example` | **PASS** | File inspect | Parameter names, ClickHouse HTTP ports 8123/8443, and stdio MCP transport settings without secrets. |
| **Health / Readiness Endpoint** | `backend/app/main.py` (`/api/v1/health`) | **PASS** | `GET /api/v1/health` | Exposes provider configuration state and model details. |
