# 🏗️ CineVector Vault — Architecture Whitepaper (ClickHouse Track)

## 1. System Overview
**CineVector Vault** is a video intelligence and vector continuity engine powered by **Google Gemini 2.0** and the **ClickHouse MCP Server** (`mcp-clickhouse`). It solves character facial, wardrobe, and lighting drift across AI-generated video shots.

```mermaid
graph TD
    User([🎬 User / Script Supervisor]) --> UI[🖥️ Interactive Web UI<br/>Shot & Scene Selector]
    UI --> GeminiAgent[🤖 Gemini 2.0 Visual Feature Extractor<br/>(Extracts costume, lighting & facial tokens)]
    GeminiAgent --> ClickHouseAgent[🛡️ ContinuitySentinel Agent]
    ClickHouseAgent --> ClickHouseMCP[🗄️ ClickHouse MCP Server<br/>(mcp-clickhouse)]
    ClickHouseMCP --> ClickHouseDB[(ClickHouse MergeTree<br/>Reference Vectors)]
    ClickHouseMCP --> Evidence[📊 Continuity Verification & Cosine Score]
    Evidence --> UI
```

---

## 2. End-to-End Execution Flow
1. **Shot Input**: User inputs a new scene description or prompt for character "Maya Vance".
2. **Gemini 2.0 Extraction**: Calls `google-genai` to deconstruct the shot into structured attributes (costume items, lighting palette, keypoints).
3. **ClickHouse MCP Query**: Calls `clickhouse_search_vector_continuity` over indexed MergeTree reference shots.
4. **Continuity Scoring**: Computes vector cosine similarity and returns verified status or flags drift.
5. **UI Display**: Renders extracted tokens, matched reference frames, similarity percentage, and locally measured latency.
