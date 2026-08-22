# 🏗️ CineVector Vault — Architecture Whitepaper (ClickHouse Track)

## 1. System Overview
**CineVector Vault** is a video intelligence and vector continuity engine powered by **Google Gemini 3.7 Flash** and the official **ClickHouse MCP Server (`mcp-clickhouse`)**. It evaluates character facial, wardrobe, and lighting drift across AI-generated video shots.

```mermaid
graph TD
    User([🎬 User / Script Supervisor]) --> UI[🖥️ Interactive Web UI<br/>Shot & Scene Selector]
    UI --> GeminiAgent[🤖 Gemini 3.7 Flash Visual Feature Extractor<br/>(Extracts costume, lighting & facial tokens)]
    GeminiAgent --> ClickHouseAgent[🛡️ ContinuitySentinel Agent]
    ClickHouseAgent --> ClickHouseMCP[🗄️ Official ClickHouse MCP Client<br/>(mcp-clickhouse via Python MCP SDK stdio)]
    ClickHouseMCP --> ClickHouseDB[(ClickHouse MergeTree<br/>Reference Vectors)]
    ClickHouseMCP --> Evidence[📊 Continuity Verification & Cosine Score]
    Evidence --> UI
```

---

## 2. End-to-End Execution Flow
1. **Shot Input**: User inputs a new scene description or prompt for character "Maya Vance".
2. **Gemini 3.7 Flash Extraction**: Calls `google-genai` to deconstruct the shot into structured attributes (costume items, lighting palette, keypoints).
3. **ClickHouse MCP Query**: Invokes official `mcp-clickhouse` server via stdio transport using `run_query` over indexed MergeTree reference shots.
4. **Continuity Scoring**: Computes vector cosine similarity and returns verified status or flags drift.
5. **UI Display**: Renders extracted tokens, matched reference frames, similarity percentage, and measured latency.
