import logging
import time
from typing import Dict, Any, List
from app.services.gemini_service import gemini_service
from app.mcp.clickhouse_mcp_server import clickhouse_mcp_server

logger = logging.getLogger("cinevector.continuity_agent")

class ContinuityAgent:
    """
    Autonomous Character Continuity Agent powered by Gemini 3.7 Flash and official mcp-clickhouse.
    Extracts structured visual tokens via Gemini 3.7 Flash, then executes
    vector similarity matching against ClickHouse reference tables using official MCP tools.
    """
    def __init__(self):
        self.name = "ContinuitySentinel"
        self.role = "Visual Continuity & Vector Match Inspector"

    async def verify_shot_continuity(self, character: str, shot_description: str) -> Dict[str, Any]:
        start = time.time()
        
        # Step 1: Gemini 3.7 Flash Visual Feature Extraction
        gemini_res = gemini_service.extract_continuity_tokens(character, shot_description)
        if not gemini_res.get("success"):
            return {
                "agent": self.name,
                "character": character,
                "status": "LIVE_ERROR",
                "mode": gemini_res.get("mode", "live_error"),
                "error": gemini_res.get("error", "Gemini extraction failed"),
                "gemini_evidence_source": gemini_res.get("evidence_source"),
                "clickhouse_evidence_source": "mcp-clickhouse (Not Reached)",
                "measured_latency_ms": round((time.time() - start) * 1000, 2)
            }

        extracted_tokens = gemini_res.get("data", {})

        # Step 2: ClickHouse MCP Vector Similarity Search
        vector_res = await clickhouse_mcp_server.call_tool(
            "clickhouse_search_vector_continuity",
            {"character": character, "query_tokens": extracted_tokens}
        )

        if vector_res.get("status") == "error":
            return {
                "agent": self.name,
                "character": character,
                "status": "LIVE_ERROR",
                "mode": vector_res.get("mode", "live_error"),
                "error": vector_res.get("error", "ClickHouse MCP query failed"),
                "gemini_extracted_tokens": extracted_tokens,
                "gemini_evidence_source": gemini_res.get("evidence_source"),
                "clickhouse_evidence_source": vector_res.get("evidence_source"),
                "measured_latency_ms": round((time.time() - start) * 1000, 2)
            }

        top_matches = vector_res.get("top_matches", [])
        avg_score = top_matches[0].get("similarity_score", 0.85) if top_matches else 0.80
        status = "PASSED_CONTINUITY" if avg_score >= 0.85 else "DRIFT_DETECTED"

        return {
            "agent": self.name,
            "character": character,
            "status": status,
            "mode": vector_res.get("mode", gemini_res.get("mode", "demo")),
            "cosine_similarity": avg_score,
            "gemini_extracted_tokens": extracted_tokens,
            "gemini_evidence_source": gemini_res.get("evidence_source"),
            "clickhouse_evidence_source": vector_res.get("evidence_source"),
            "checked_shots_count": len(top_matches),
            "reference_matches": top_matches,
            "measured_latency_ms": round((time.time() - start) * 1000, 2)
        }

continuity_agent = ContinuityAgent()
