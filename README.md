<div align="center">

# 🗄️ CineVector Vault
### Columnar Video Intelligence & Vector Continuity Media Lake
**Built for the ClickHouse Track — Google Cloud "Agentic Cinema: The Blockbuster Hackathon"**

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![ClickHouse MCP](https://img.shields.io/badge/ClickHouse-mcp--clickhouse-FFCC01?logo=clickhouse&logoColor=black)](https://clickhouse.com)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-3.7%20Flash-4285F4?logo=google&logoColor=white)](https://cloud.google.com/vertex-ai)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)

</div>

---

## 🌟 Overview
**CineVector Vault** is a multimodal media data lake and vector continuity search engine. The default public evaluator uses deterministic local fixtures. Official **mcp-clickhouse** connected to a live ClickHouse cluster and **Gemini 3.7 Flash** are implemented as live integration paths. Official mcp-clickhouse was proven against managed ClickHouse Cloud 26.2.1.558 and, independently, a self-hosted ClickHouse 25.8.31.9 cluster. The current Gemini path targets 3.7 Flash; the separate authenticated Gemini smoke used 2.5 Flash and proves the SDK path, not a 3.7 call. It addresses a key challenge in AI filmmaking: detecting character wardrobe, facial, and lighting drift across video takes.

---

## 🚀 Key Features

1. **⚡ Columnar Vector Continuity Search**:
   - Executes `cosineDistance` vector queries over 768-dim video frame embeddings using ClickHouse's vector distance functions.
   - Evaluates character wardrobe and lighting consistency between AI-generated shots.

2. **🗄️ MergeTree Columnar Schemas**:
   - `video_frames`: Cataloged reference takes, timestamps, and embeddings.
   - `script_dialogues`: Semantic full-text search across dialogue transcripts.

3. **🔌 Official `mcp-clickhouse` Integration**:
   - Direct runtime MCP integration using the official Python MCP SDK and `mcp-clickhouse` server package.
   - Leverages official MCP tools: `run_query`, `list_databases`, `list_tables`.

4. **🤖 Specialized Gemini 3.7 Agent Crew**:
   - **ContinuitySentinel Agent**: Extracts visual attributes via Gemini 3.7 Flash and verifies vector match consistency.
   - **VideoIndexer Agent**: Indexes video rush takes into ClickHouse tables.
   - **Analytics Agent**: Delivers studio KPI reports and SQL performance metrics.

---

## ⚙️ Configuration & Connection Settings

### ClickHouse Database Ports
- **Port 8123**: Standard unencrypted HTTP protocol port.
- **Port 8443**: Standard HTTPS/TLS secure port (default for ClickHouse secure connections).

### Official MCP Transport Settings
- The application uses a managed **stdio session** via the official Python `mcp` SDK to launch the installed `mcp-clickhouse` server process.
- Environment variables (`CLICKHOUSE_HOST`, `CLICKHOUSE_PORT`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`, `CLICKHOUSE_SECURE`) are passed directly into the stdio session environment.

---

## ⚡ Clean Clone Quickstart

```bash
# 1. Clone repository & navigate to backend
cd backend

# 2. Install dependencies (includes mcp and mcp-clickhouse)
pip install -r requirements.txt

# 3. Configure environment
cp ../.env.example .env
# Edit .env to set RUNTIME_MODE=demo (local fixture) or RUNTIME_MODE=live (Live ClickHouse cluster + Gemini credentials)

# 4. Start backend server
python run_backend.py
```
* Interactive Studio Web UI available at: `http://localhost:8001/`
* OpenAPI Swagger docs available at: `http://localhost:8001/docs`

---

## 🧪 Testing

```bash
cd backend
python -m pytest -q
```

---

## 📄 License
Licensed under the **[MIT License](LICENSE)**.

## 🚀 Public Deployment (Vercel)

**Live judge demo:** https://cinevector-vault.vercel.app/  
**Public source:** https://github.com/AtchayamG/cinevector-vault

The stable Vercel judge URL proxies the latest Cloud Run backend. Public health reports `runtime_mode: hybrid`: Gemini 3.7 Flash is live through Vertex AI ADC, while ClickHouse remains explicitly labeled demo until production ClickHouse credentials are connected. Separate authenticated `mcp-clickhouse` evidence is documented in the repository.

1. Import your project into Vercel.
2. In the project settings, set the **Root Directory** to `backend`.
3. Vercel will automatically use `backend/vercel.json` and deploy `app.main:app` via `@vercel/python`.

