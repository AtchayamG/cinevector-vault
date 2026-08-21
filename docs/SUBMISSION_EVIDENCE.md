# 📋 Submission Evidence Matrix: Track 2 (ClickHouse Track)

| Official Requirement | Implementation / Evidence Path | Status | Verification Command | Truthful Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Active Runtime Gemini 2.0 Usage** | `backend/app/services/gemini_service.py`<br/>`backend/app/agents/continuity_agent.py` | **PASS** | `pytest tests/test_clickhouse_vault.py` | Calls `google-genai` SDK for visual feature extraction from scene descriptions. |
| **Official ClickHouse MCP Integration** | `backend/app/mcp/clickhouse_mcp_server.py`<br/>`backend/app/services/clickhouse_service.py` | **PASS** (Local Fixtures) / **BLOCKED** (Live Cloud Password) | `pytest tests/test_clickhouse_vault.py` | Implements `mcp-clickhouse` JSON-RPC tool contracts and MergeTree schemas. |
| **Judge-Friendly Web UI** | `backend/app/static/index.html`<br/>`backend/app/main.py` | **PASS** | Open `http://localhost:8001/` | Interactive web studio with Shot Ingestion, Gemini Extraction Inspector, ClickHouse Vector Matcher, and SQL Console. |
| **Explicit Live / Demo Mode** | `backend/app/config.py`<br/>`backend/app/services/clickhouse_service.py` | **PASS** | `pytest tests/test_clickhouse_vault.py` | Clear `MODE: DEMO` badge and honest evidence source tags. |
| **Small Reproducible Seed Dataset** | `backend/app/services/clickhouse_service.py` | **PASS** | File inspect | 3 reference shots with embeddings across Maya Vance and Dr. Chen. |
| **Open Source License** | `LICENSE` | **PASS** | File inspect | Apache 2.0 Open Source License. |
| **Environment Template** | `.env.example` | **PASS** | File inspect | Parameter names and explanations without secrets. |
| **Health / Readiness Endpoint** | `backend/app/main.py` (`/api/v1/health`) | **PASS** | `GET /api/v1/health` | Exposes provider configuration state. |
