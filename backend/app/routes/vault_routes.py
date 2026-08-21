from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List
from app.services.clickhouse_service import clickhouse_service
from app.agents.continuity_agent import continuity_agent
from app.agents.video_indexer_agent import video_indexer_agent
from app.agents.analytics_agent import analytics_agent
from app.mcp.clickhouse_mcp_server import clickhouse_mcp_server

router = APIRouter(prefix="/vault", tags=["CineVector Vault API"])

class VectorSearchRequest(BaseModel):
    character: str = "Maya Vance"
    min_similarity: float = 0.90

class SQLQueryRequest(BaseModel):
    sql: str = "SELECT * FROM video_frames LIMIT 10"

class IngestSceneRequest(BaseModel):
    movie_id: str = "NEON_HORIZONS"
    scene_number: int = 1
    frame_count: int = 1200

@router.post("/search/continuity")
async def verify_continuity(req: VectorSearchRequest):
    return await continuity_agent.verify_shot_continuity(req.character, "Shot inspection")

@router.post("/sql")
async def execute_sql(req: SQLQueryRequest):
    return clickhouse_service.execute_sql(req.sql)

@router.post("/ingest")
async def ingest_frames(req: IngestSceneRequest):
    return await video_indexer_agent.ingest_scene_takes(req.movie_id, req.scene_number, req.frame_count)

@router.get("/kpis")
async def get_kpis():
    return await analytics_agent.get_production_kpis()

@router.get("/mcp/tools")
async def get_mcp_tools():
    return {
        "server": "mcp-clickhouse",
        "tools": clickhouse_mcp_server.list_tools()
    }
