# 🤝 Agent Handoff Document: Track 2 (ClickHouse Track)

**Target Hackathon:** Google Cloud "Agentic Cinema: The Blockbuster Hackathon" (Devpost)  
**Assigned Category:** **ClickHouse Track** ($7,500 1st Place)  
**Application Name:** **`CineVector Vault`**  
**Submitting Status:** ✅ READY FOR SUBMISSION  

---

## 1. Executive Summary & Purpose
**CineVector Vault** is a multimodal video data lake and vector continuity engine powered by official **ClickHouse MCP (`mcp-clickhouse`)** and **Gemini 2.5 Flash**. It helps detect and reduce character facial, wardrobe, and lighting drift across consecutive shots.

Using ClickHouse's MergeTree engine and `cosineDistance` vector scans over 768-dim embeddings, autonomous agents catalog video takes and maintain character consistency.

---

## 2. Devpost Submission Fields (Copy-Paste Ready)
- **Project Title:** `CineVector Vault: Columnar Video Intelligence & Vector Continuity Media Lake`
- **Elevator Pitch:** `A multimodal media data lake powered by official ClickHouse MCP (mcp-clickhouse) and Gemini 2.5 Flash that catalog video frames and dialogue transcripts, enabling columnar vector similarity search to detect and help reduce AI character drift and power real-time film studio analytics.`
- **Partner Track:** `ClickHouse Track`
- **License:** `Apache 2.0` (Included at root)

---

## 3. Codebase Architecture & File Map
```
Track2_ClickHouse_CineVector_Vault/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── continuity_agent.py        # Vector similarity & character drift detector
│   │   │   ├── video_indexer_agent.py     # Frame token ingestion agent
│   │   │   └── analytics_agent.py         # Production KPI & data lake reporter
│   │   ├── mcp/
│   │   │   └── clickhouse_mcp_server.py   # Official mcp-clickhouse Python SDK stdio client
│   │   ├── services/
│   │   │   └── clickhouse_service.py      # Direct clickhouse-connect client for bootstrap
│   │   ├── routes/vault_routes.py         # API endpoints (/vault/search, /vault/sql, /vault/ingest, /vault/kpis)
│   │   ├── config.py & main.py            # Configuration & FastAPI entrypoint
│   │   └── run_backend.py                 # Runner script
│   └── tests/test_clickhouse_vault.py     # Automated pytest suite
├── docs/
│   ├── DEVPOST_SUBMISSION.md              # Full Devpost submission details
│   ├── AGY_HANDOFF.md                     # AntiGravity to Integrator Handoff
│   └── AGENT_HANDOFF.md                   # This handoff guide
├── LICENSE                                # Apache 2.0
└── README.md                              # Main documentation
```

---

## 4. Verification & Testing Commands

### A. Run Automated Backend Tests
```bash
cd backend
python -m pytest -v
```

### B. Run Backend Server
```bash
python run_backend.py
# Server starts on http://localhost:8001 (Swagger docs at /docs)
```

### C. Test Sample Vector Search API Call
```bash
curl -X POST "http://localhost:8001/api/v1/vault/search/continuity" -H "Content-Type: application/json" -d "{\"character\": \"Maya Vance\", \"shot_description\": \"Maya Vance in rain coat\", \"min_similarity\": 0.85}"
```
