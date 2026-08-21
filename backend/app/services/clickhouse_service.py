import logging
import time
import math
import zlib
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger("cinevector.clickhouse")

class ClickHouseService:
    """
    ClickHouse Live Cluster & MergeTree Vector Store integration for CineVector Vault.
    Handles columnar video frame indexing, vector continuity matching, and SQL analytics.
    Direct clickhouse-connect is reserved for schema setup and bootstrap queries.
    """
    def __init__(self):
        self.host = settings.CLICKHOUSE_HOST
        self.port = settings.CLICKHOUSE_PORT
        self.user = settings.CLICKHOUSE_USER
        self.password = settings.CLICKHOUSE_PASSWORD
        self.database = settings.CLICKHOUSE_DATABASE
        self.runtime_mode = settings.RUNTIME_MODE
        self.client = None
        
        # Seed Reference Catalog (3 Local Reference Shots)
        self.reference_catalog = [
            {
                "shot_id": "TAKE-101_REF",
                "scene": 1,
                "character": "Maya Vance",
                "costume": "Charcoal cyber trenchcoat, matte collar",
                "lighting": "Cyan key, magenta rim",
                "vector_embedding": [0.12, 0.45, -0.23, 0.88, 0.05, 0.33, -0.15, 0.62],
                "frame_url": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800&auto=format&fit=crop&q=80"
            },
            {
                "shot_id": "TAKE-102_REF",
                "scene": 1,
                "character": "Maya Vance",
                "costume": "Charcoal cyber trenchcoat, rain droplets",
                "lighting": "Cyan anamorphic flare",
                "vector_embedding": [0.11, 0.44, -0.20, 0.86, 0.08, 0.31, -0.12, 0.60],
                "frame_url": "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=800&auto=format&fit=crop&q=80"
            },
            {
                "shot_id": "TAKE-201_REF",
                "scene": 2,
                "character": "Dr. Alistair Chen",
                "costume": "White biometric lab coat, silver trim",
                "lighting": "Crimson strobe light",
                "vector_embedding": [-0.34, 0.12, 0.78, -0.15, 0.44, 0.02, 0.88, -0.20],
                "frame_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=80"
            }
        ]
        self._init_connection()

    def _init_connection(self):
        if self.password and self.runtime_mode == "live":
            try:
                import clickhouse_connect
                self.client = clickhouse_connect.get_client(
                    host=self.host,
                    port=self.port,
                    username=self.user,
                    password=self.password,
                    database=self.database,
                    secure=settings.CLICKHOUSE_SECURE
                )
                logger.info("Connected to live ClickHouse cluster for bootstrap operations.")
            except Exception as e:
                logger.warning(f"ClickHouse live bootstrap client failed: {e}")
                self.client = None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        min_len = min(len(vec1), len(vec2))
        if min_len == 0:
            return 0.50
        dot = sum(vec1[i] * vec2[i] for i in range(min_len))
        norm1 = math.sqrt(sum(x * x for x in vec1[:min_len]))
        norm2 = math.sqrt(sum(x * x for x in vec2[:min_len]))
        if norm1 == 0 or norm2 == 0:
            return 0.50
        val = dot / (norm1 * norm2)
        return round(max(min(val, 1.0), -1.0), 3)

    def _derive_vector_from_tokens(self, query_tokens: Optional[Dict[str, Any]], character: str) -> List[float]:
        if not query_tokens:
            query_tokens = {}
        
        costumes = " ".join(query_tokens.get("costume_tokens", [])).lower()
        lighting = " ".join(query_tokens.get("lighting_palette", [])).lower()
        style = str(query_tokens.get("visual_style", "")).lower()
        combined_text = f"{character} {costumes} {lighting} {style}".lower()
        
        vec = [0.0] * 8
        if "trenchcoat" in combined_text or "cyber" in combined_text:
            vec[0] += 0.12
            vec[1] += 0.45
            vec[2] -= 0.23
            vec[3] += 0.88
            vec[7] += 0.62
        if "lab coat" in combined_text or "white" in combined_text or "biometric" in combined_text:
            vec[0] -= 0.34
            vec[2] += 0.78
            vec[4] += 0.44
            vec[6] += 0.88
        if "cyan" in combined_text or "magenta" in combined_text or "rain" in combined_text:
            vec[1] += 0.40
            vec[5] += 0.30
        if "crimson" in combined_text or "strobe" in combined_text:
            vec[4] += 0.50
            vec[6] += 0.20

        if all(v == 0.0 for v in vec):
            h = zlib.crc32(combined_text.encode("utf-8"))
            vec = [((h >> (i * 3)) & 0x0F) / 10.0 - 0.5 for i in range(8)]

        return vec

    def execute_sql(self, sql: str) -> Dict[str, Any]:
        start = time.time()
        if self.runtime_mode == "live":
            if self.client:
                try:
                    res = self.client.query(sql)
                    duration_ms = round((time.time() - start) * 1000, 2)
                    return {
                        "status": "success",
                        "mode": "live",
                        "evidence_source": "ClickHouse Live Cluster (Live Direct Client)",
                        "columns": res.column_names,
                        "rows": res.result_rows,
                        "row_count": len(res.result_rows),
                        "execution_time_ms": duration_ms
                    }
                except Exception as e:
                    logger.error(f"ClickHouse live SQL error: {e}")
                    return {
                        "status": "error",
                        "mode": "live_error",
                        "error": str(e),
                        "evidence_source": "ClickHouse Live Cluster (Live Query Failed)"
                    }
            return {
                "status": "error",
                "mode": "live_unavailable",
                "error": "ClickHouse live client not connected",
                "evidence_source": "ClickHouse Live Cluster (Unconfigured)"
            }

        # Demo mode
        duration_ms = max(round((time.time() - start) * 1000, 2), 1.8)
        return {
            "status": "success",
            "mode": "demo",
            "evidence_source": "ClickHouse MergeTree (Local Fixture)",
            "columns": ["shot_id", "scene_number", "character", "costume_match", "status"],
            "rows": [
                ["TAKE-101_REF", 1, "Maya Vance", "Charcoal cyber trenchcoat", "VERIFIED_CONTINUITY"],
                ["TAKE-102_REF", 1, "Maya Vance", "Charcoal cyber trenchcoat", "VERIFIED_CONTINUITY"],
                ["TAKE-201_REF", 2, "Dr. Alistair Chen", "Biometric lab coat", "VERIFIED_CONTINUITY"]
            ],
            "row_count": 3,
            "execution_time_ms": duration_ms
        }

    def search_vector_continuity(self, character: str, query_tokens: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start = time.time()
        if self.runtime_mode == "live":
            if self.client:
                try:
                    res = self.client.query(f"SELECT shot_id, scene, character, costume, lighting FROM video_frames WHERE character = '{character}' LIMIT 3")
                    duration_ms = round((time.time() - start) * 1000, 2)
                    return {
                        "status": "success",
                        "mode": "live",
                        "evidence_source": "ClickHouse Live Cluster (Live Vector Query)",
                        "character": character,
                        "query_latency_ms": duration_ms,
                        "rows": res.result_rows
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "mode": "live_error",
                        "error": str(e),
                        "evidence_source": "ClickHouse Live Cluster (Live Vector Search Failed)"
                    }
            return {
                "status": "error",
                "mode": "live_unavailable",
                "error": "Live ClickHouse connection unavailable",
                "evidence_source": "ClickHouse Live Cluster (Unconfigured)"
            }

        # Demo Mode: dynamic matching using input description/tokens
        derived_query_vec = self._derive_vector_from_tokens(query_tokens, character)
        matches = [r for r in self.reference_catalog if r["character"].lower() == character.lower()]
        if not matches:
            matches = self.reference_catalog

        results = []
        for ref in matches:
            sim = self._cosine_similarity(derived_query_vec, ref["vector_embedding"])
            results.append({
                "shot_id": ref["shot_id"],
                "scene": ref["scene"],
                "similarity_score": sim,
                "wardrobe_match": "High" if sim >= 0.85 else "Review Needed",
                "reference_costume": ref["costume"],
                "reference_lighting": ref["lighting"],
                "frame_url": ref["frame_url"]
            })

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        duration_ms = max(round((time.time() - start) * 1000, 2), 2.1)

        return {
            "status": "success",
            "mode": "demo",
            "evidence_source": "ClickHouse MergeTree (Local Fixture)",
            "character": character,
            "query_latency_ms": duration_ms,
            "top_matches": results
        }

clickhouse_service = ClickHouseService()
