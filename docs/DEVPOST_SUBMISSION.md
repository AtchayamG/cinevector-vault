# 🎬 Devpost Submission: CineVector Vault (ClickHouse Track)

## Project Name
**CineVector Vault: Columnar Video Intelligence & Vector Continuity Media Lake**

## Elevator Pitch
A multimodal media data lake powered by official ClickHouse MCP (`mcp-clickhouse`) and Gemini 3.7 Flash that catalog video frames and dialogue transcripts, enabling columnar vector similarity search to detect and help reduce AI character drift and power real-time film studio analytics.

## Selected Track
**ClickHouse Track** ($7,500 1st Place)

## Judge Links
- **Live Application:** https://cinevector-vault.vercel.app/
- **Public Repository:** https://github.com/AtchayamG/cinevector-vault
- **Demo Video:** https://youtu.be/jOU1YCBdTnA
- **Supplemental Cinematic Evidence:** https://youtu.be/pbyWb7vMHT4 — fixed, pre-generated Veo continuity reel; ClickHouse live integration is demonstrated separately in the application and primary demo.
- **Runtime Note:** The public evaluator runs Gemini 3.7 Flash through Vertex AI and official `mcp-clickhouse` against ClickHouse Cloud using a dedicated read-only database identity. Public end-to-end evidence is recorded in `docs/evidence/PUBLIC_RUNTIME_VERIFICATION_2026-08-30.md`.

## What It Does
1. **Columnar Vector Search**: Uses ClickHouse's vector distance functions to compute cosine similarity across 768-dim frame embeddings.
2. **AI Character Continuity**: Evaluates character generated across separate shots to maintain consistent faces, wardrobe, and lighting.
3. **Multimodal Video Ingestion**: Ingests video rushes into ClickHouse MergeTree tables.
4. **Official ClickHouse MCP (`mcp-clickhouse`)**: Integrates official `mcp-clickhouse` server via Python MCP SDK stdio transport (`run_query`, `list_databases`, `list_tables`).
