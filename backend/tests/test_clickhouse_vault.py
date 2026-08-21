import pytest
from app.services.gemini_service import gemini_service
from app.services.clickhouse_service import clickhouse_service
from app.agents.continuity_agent import continuity_agent
from app.agents.video_indexer_agent import video_indexer_agent
from app.mcp.clickhouse_mcp_server import clickhouse_mcp_server

@pytest.mark.asyncio
async def test_mcp_tool_list():
    tools = clickhouse_mcp_server.list_tools()
    assert len(tools) >= 3
    tool_names = [t["name"] for t in tools]
    assert "clickhouse_execute_sql" in tool_names
    assert "clickhouse_search_vector_continuity" in tool_names

@pytest.mark.asyncio
async def test_gemini_token_extraction():
    res = gemini_service.extract_continuity_tokens("Maya Vance", "35mm shot in cyan rain coat")
    assert res["success"] is True
    assert "data" in res
    assert "costume_tokens" in res["data"]
    assert "lighting_palette" in res["data"]

@pytest.mark.asyncio
async def test_continuity_agent_flow():
    res = await continuity_agent.verify_shot_continuity("Maya Vance", "35mm shot in cyan rain coat")
    assert res["status"] in ("PASSED_CONTINUITY", "DRIFT_DETECTED")
    assert "gemini_extracted_tokens" in res
    assert len(res["reference_matches"]) > 0
    assert "measured_latency_ms" in res

@pytest.mark.asyncio
async def test_clickhouse_sql_demo_query():
    res = clickhouse_service.execute_sql("SELECT shot_id, scene_number FROM video_frames")
    assert res["status"] == "success"
    assert "rows" in res
    assert res["row_count"] > 0
