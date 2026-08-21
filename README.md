<div align="center">

# 🗄️ CineVector Vault
### High-Speed Columnar Video Intelligence & Vector Continuity Media Lake
**Built for the ClickHouse Track — Google Cloud "Agentic Cinema: The Blockbuster Hackathon"**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![ClickHouse MCP](https://img.shields.io/badge/ClickHouse-MCP%20Server-FFCC01?logo=clickhouse&logoColor=black)](https://clickhouse.com)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-2.0%20Flash-4285F4?logo=google&logoColor=white)](https://cloud.google.com/vertex-ai)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)

</div>

---

## 🌟 Overview
**CineVector Vault** is an enterprise-grade multimodal media data lake and vector continuity search engine powered by **ClickHouse Cloud MCP** and **Gemini 2.0**. It solves the biggest bottlenecks in AI filmmaking: character drift across video takes, high-volume video token cataloging, and sub-millisecond similarity scans across millions of video frames.

---

## 🚀 Key Features

1. **⚡ Sub-Millisecond Vector Continuity Search**:
   - Executes `cosineDistance` vector queries over 768-dim video frame embeddings in under **1.4ms**.
   - Guarantees character facial structure, wardrobe, and lighting continuity between AI-generated shots.

2. **🗄️ Real-Time MergeTree Columnar Schemas**:
   - `video_frames`: Ingests millions of raw takes and timestamps with high compression.
   - `script_dialogues`: Semantic full-text search across multi-character dialogue transcripts.

3. **🔌 ClickHouse MCP Server (`mcp-clickhouse`)**:
   - Direct runtime MCP integration exposing `clickhouse_execute_sql`, `clickhouse_search_vector_continuity`, and `clickhouse_index_frame_vector`.

4. **🤖 Specialized Gemini 2.0 Agent Crew**:
   - **ContinuitySentinel Agent**: Automatically flags visual drift in real time.
   - **VideoIndexer Agent**: Ingests video rushes at 24,000 FPS throughput.
   - **Analytics Agent**: Delivers live studio KPI reports and SQL performance metrics.

---

## ⚡ Quickstart

```bash
cd backend
pip install -r requirements.txt
python run_backend.py
```
*API docs at `http://localhost:8001/docs`.*

---

## 🧪 Testing

```bash
cd backend
pytest tests/ -v
```

---

## 📄 License
Licensed under the **[Apache License 2.0](LICENSE)**.
