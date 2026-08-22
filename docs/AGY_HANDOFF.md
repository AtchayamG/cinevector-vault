# 🤖 AntiGravity Handoff Document: Track 2 (ClickHouse Track)

> Historical note: this handoff records the earlier Gemini 2.5 hardening pass. The current implementation and judge-facing materials use `gemini-3.7-flash`; see `docs/AGENT_HANDOFF.md` and `docs/SUBMISSION_EVIDENCE.md` for current state.

## Result
CineVector Vault has been updated to be fully truthful for the ClickHouse track. The default public evaluator uses deterministic local fixtures. Official `mcp-clickhouse` and Gemini 2.5 Flash are implemented as live integration paths. Official mcp-clickhouse was proven against self-hosted ClickHouse 25.8.31.9, and the independent Gemini service smoke passed. The previous mock wrapper was replaced with an official MCP client path using the official Python `mcp` SDK and installed `mcp-clickhouse` server package via a managed stdio session. All unmeasured scale/throughput claims (e.g. 24,000 FPS, sub-millisecond, petabytes) were removed from code, UI, README, handoffs, Devpost draft, and video script. All Gemini model labels were updated to stable `gemini-2.5-flash`. Tailwind CDN was replaced with local CSS, and an embedded SVG favicon was added to prevent console 404s.

## Files Changed
- `backend/requirements.txt`: Added `mcp>=1.2.0` and `mcp-clickhouse>=0.4.0`.
- `backend/app/config.py`: Updated default model to `gemini-2.5-flash` and refined live configuration checks.
- `backend/app/mcp/clickhouse_mcp_server.py`: Replaced custom wrapper with official `ClickHouseMCPClient` connecting to `mcp-clickhouse` server via stdio transport using official MCP SDK and registering real tools (`run_query`, `list_databases`, `list_tables`).
- `backend/app/services/clickhouse_service.py`: Restricted `clickhouse-connect` to bootstrap operations, enforced strict `live_error`/`live_unavailable` reporting without silent fallback, and implemented dynamic input-dependent vector similarity matching in demo mode.
- `backend/app/services/gemini_service.py`: Updated model to `gemini-2.5-flash`, enforced strict `live_error`/`live_unavailable` reporting in live mode, and added dynamic prompt token extraction for demo mode.
- `backend/app/agents/continuity_agent.py`: Integrated Gemini 2.5 Flash and official ClickHouse MCP tools with strict live error handling.
- `backend/app/agents/analytics_agent.py`: Removed unmeasured claims and integrated `run_query` MCP tool.
- `backend/app/agents/video_indexer_agent.py`: Removed 24,000 FPS claim and integrated `run_query` MCP tool.
- `backend/app/routes/vault_routes.py`: Passed shot descriptions to continuity agent and routed SQL via official MCP `run_query` tool.
- `backend/app/main.py`: Updated app metadata to Gemini 2.5 Flash and official `mcp-clickhouse`, added `/favicon.ico` 204 handler.
- `backend/app/static/index.html`: Replaced Tailwind CDN with repository-local CSS, added embedded SVG favicon, updated labels to Gemini 2.5 Flash / `mcp-clickhouse`.
- `backend/tests/test_clickhouse_vault.py`: Added focused test suite proving official MCP session initialization, live failure blocking, Gemini failure blocking, dynamic demo input variations, honest health config, and UI endpoint success.
- `.env.example`: Updated model to `gemini-2.5-flash` and added documentation for ClickHouse ports 8123/8443 and stdio MCP transport settings.
- `README.md`: Updated badges, overview, features, installation quickstart, port explanations, and MCP transport details.
- `docs/*.md`: Updated evidence matrix, architecture whitepaper, Devpost draft, demo video script, and agent handoffs.

## Verification
- `pytest tests/ -v`: 100% Passed (9/9 tests passed).
- `gitleaks dir --no-banner --redact .`: 0 leaks found.
- Browser smoke test: `GET /`, `GET /api/v1/health`, `POST /api/v1/vault/search/continuity`, `POST /api/v1/vault/sql` all return HTTP 200 clean success with zero console errors or favicon 404s.

## Live ClickHouse Cluster Verification
- Proof was completed against self-hosted ClickHouse 25.8.31.9 through official `mcp-clickhouse`.
- **Reproduction Instructions**: To reproduce the live ClickHouse cluster proof, provide `CLICKHOUSE_HOST` and `CLICKHOUSE_PASSWORD` in `.env` along with `GEMINI_API_KEY`, set `RUNTIME_MODE=live`, and execute an authenticated smoke call.

## Risks
- Live execution requires network connectivity to a live ClickHouse cluster and Google GenAI API endpoints. If credentials or network connection are unavailable, system correctly reports `live_unavailable` / `live_error` as required.

## Notes For Integrator
- ClickHouse HTTP Port 8123 is unencrypted, whereas Port 8443 uses TLS/HTTPS (standard for secure remote clusters).
- The official `mcp-clickhouse` server process is executed as a managed stdio subprocess using `sys.executable -m mcp_clickhouse.main` (or `mcp-clickhouse` executable), configured via environment variables.
