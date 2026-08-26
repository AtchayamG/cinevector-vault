import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.services.gemini_service import gemini_service
from app.services.clickhouse_service import clickhouse_service
from app.agents.continuity_agent import continuity_agent
from app.agents.video_indexer_agent import video_indexer_agent
from app.mcp.clickhouse_mcp_server import clickhouse_mcp_server, OFFICIAL_MCP_TOOLS

client = TestClient(app)

@pytest.mark.asyncio
async def test_official_mcp_tools_list():
    tools = clickhouse_mcp_server.list_tools()
    tool_names = [t["name"] for t in tools]
    assert "run_query" in tool_names
    assert "list_databases" in tool_names
    assert "list_tables" in tool_names

@pytest.mark.asyncio
async def test_mcp_run_query_execution():
    res = await clickhouse_mcp_server.call_tool("run_query", {"query": "SELECT shot_id FROM video_frames"})
    assert res["status"] == "success"
    assert "evidence_source" in res
    assert "rows" in res or "mcp_output" in res

@pytest.mark.asyncio
async def test_live_failure_cannot_fall_back():
    original_mode = settings.RUNTIME_MODE
    try:
        settings.RUNTIME_MODE = "live"
        res = await clickhouse_mcp_server.call_tool("run_query", {"query": "SELECT 1"})
        assert res["status"] == "error"
        assert res["mode"] in ("live_error", "live_unavailable")
        assert res["mode"] != "demo"
    finally:
        settings.RUNTIME_MODE = original_mode

@pytest.mark.asyncio
async def test_gemini_live_failure_cannot_fall_back():
    original_mode = gemini_service.runtime_mode
    original_client = gemini_service.client
    try:
        gemini_service.runtime_mode = "live"
        gemini_service.client = None
        res = gemini_service.extract_continuity_tokens("Maya Vance", "Shot prompt")
        assert res["success"] is False
        assert res["mode"] in ("live_error", "live_unavailable")
        assert res["mode"] != "demo"
    finally:
        gemini_service.runtime_mode = original_mode
        gemini_service.client = original_client

@pytest.mark.asyncio
async def test_demo_inputs_change_results():
    res_trenchcoat = await continuity_agent.verify_shot_continuity(
        "Maya Vance", "EXT. RAIN STREET - Maya Vance in a charcoal cyber trenchcoat with high collar"
    )
    res_labcoat = await continuity_agent.verify_shot_continuity(
        "Maya Vance", "INT. LAB - Maya Vance in a white biometric lab coat with silver trim"
    )
    
    assert res_trenchcoat["status"] in ("PASSED_CONTINUITY", "DRIFT_DETECTED")
    assert res_labcoat["status"] in ("PASSED_CONTINUITY", "DRIFT_DETECTED")
    
    # Verify that input descriptions produce different extracted costume tokens
    tokens1 = res_trenchcoat["gemini_extracted_tokens"].get("costume_tokens", [])
    tokens2 = res_labcoat["gemini_extracted_tokens"].get("costume_tokens", [])
    assert tokens1 != tokens2

def test_health_endpoint_honest_config():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["providers"]["google_gemini"]["model"] == settings.GEMINI_MODEL
    assert data["providers"]["clickhouse_mcp"]["server"] == "mcp-clickhouse"

def test_ui_workflow_endpoints():
    # GET UI
    ui_res = client.get("/")
    assert ui_res.status_code == 200
    assert "CineVector Vault" in ui_res.text
    assert "deterministic local reference fixtures and a simulated SQL and result contract" in ui_res.text
    
    # POST Continuity Workflow Endpoint
    cont_res = client.post(
        "/api/v1/vault/search/continuity",
        json={"character": "Maya Vance", "shot_description": "Rain scene cyber trenchcoat", "min_similarity": 0.85}
    )
    assert cont_res.status_code == 200
    assert "measured_latency_ms" in cont_res.json()
    
    # POST SQL Endpoint
    sql_res = client.post("/api/v1/vault/sql", json={"sql": "SELECT 1"})
    assert sql_res.status_code == 200
    
    # POST Ingest Endpoint
    ingest_res = client.post("/api/v1/vault/ingest", json={"movie_id": "TEST_MOVIE", "scene_number": 1, "frame_count": 50})
    assert ingest_res.status_code == 200
    
    # GET KPIs Endpoint
    kpi_res = client.get("/api/v1/vault/kpis")
    assert kpi_res.status_code == 200

@pytest.mark.asyncio
async def test_live_cluster_evidence_labels():
    original_mode = settings.RUNTIME_MODE
    original_host = settings.CLICKHOUSE_HOST
    try:
        settings.RUNTIME_MODE = "live"
        settings.CLICKHOUSE_HOST = "" # Force unconfigured state
        res = await clickhouse_mcp_server.call_tool("run_query", {"query": "SELECT 1"})
        
        evidence = res.get("evidence_source", "")
        error_msg = res.get("error", "")
        
        assert "Live Cluster" in evidence or "Live Cluster" in error_msg or "mcp-clickhouse" in evidence or "live ClickHouse credentials" in error_msg
    finally:
        settings.RUNTIME_MODE = original_mode
        settings.CLICKHOUSE_HOST = original_host

from unittest.mock import patch

@pytest.mark.asyncio
async def test_mcp_sql_injection_prevention():
    original_mode = settings.RUNTIME_MODE
    original_host = settings.CLICKHOUSE_HOST
    original_pass = settings.CLICKHOUSE_PASSWORD
    try:
        settings.RUNTIME_MODE = "live"
        settings.CLICKHOUSE_HOST = "127.0.0.1"
        settings.CLICKHOUSE_PASSWORD = "test"
        
        with patch('mcp.ClientSession') as MockSession, \
             patch('mcp.client.stdio.stdio_client') as mock_stdio:
            
            # Setup async context manager mocks
            mock_stdio.return_value.__aenter__.return_value = (None, None)
            mock_session_instance = MockSession.return_value.__aenter__.return_value
            mock_session_instance.call_tool.return_value = type('obj', (object,), {'isError': False, 'content': []})
            
            # Call the tool with an apostrophe payload
            await clickhouse_mcp_server.call_tool("clickhouse_search_vector_continuity", {"character": "Maya' OR '1'='1"})
            
            # Extract the actual query passed to call_tool
            call_args = mock_session_instance.call_tool.call_args
            assert call_args is not None, "call_tool was not called"
            args, kwargs = call_args
            called_tool_name = args[0]
            called_arguments = args[1]
            
            assert called_tool_name == "run_query"
            assert "Maya'' OR ''1''=''1" in called_arguments["query"]
            assert "Maya' OR '1'='1" not in called_arguments["query"]
    finally:
        settings.RUNTIME_MODE = original_mode
        settings.CLICKHOUSE_HOST = original_host
        settings.CLICKHOUSE_PASSWORD = original_pass
def test_ui_xss_prevention():
    ui_res = client.get('/')
    assert ui_res.status_code == 200
    assert '.innerHTML = `' not in ui_res.text
    assert 'document.createElement' in ui_res.text
    assert 'textContent' in ui_res.text

def test_api_hostile_payloads():
    hostile_html = '<script>alert("xss")</script>\"'
    cont_res = client.post(
        '/api/v1/vault/search/continuity',
        json={'character': hostile_html, 'shot_description': hostile_html, 'min_similarity': 0.85}
    )
    assert cont_res.status_code == 200
    data = cont_res.json()
    assert 'error' in data or 'status' in data

def test_demo_labels_on_paint():
    ui_res = client.get('/')
    assert ui_res.status_code == 200
    assert '1. Scene Shot Ingest & Local Deterministic Continuity Fixtures' in ui_res.text
    assert '2. Local Vector Match Similarity Fixtures' in ui_res.text
    assert '3. Local SQL Fixtures Console' in ui_res.text
    assert '⚡ Run Local Deterministic Continuity Fixtures' in ui_res.text
    assert "Local fixture matched reference shots:" in ui_res.text


def test_vertex_default_location_supports_gemini_37():
    assert settings.GOOGLE_CLOUD_LOCATION == "global"


def test_runtime_mode_defaults_and_overrides():
    orig_rm = settings.RUNTIME_MODE
    orig_gm = settings.GEMINI_RUNTIME_MODE
    orig_pm = settings.PARTNER_RUNTIME_MODE
    try:
        # Reset overrides to test defaulting
        settings.GEMINI_RUNTIME_MODE = None
        settings.PARTNER_RUNTIME_MODE = None
        settings.RUNTIME_MODE = "demo"
        
        assert settings.GEMINI_RUNTIME_MODE == "demo"
        assert settings.PARTNER_RUNTIME_MODE == "demo"
        assert settings.effective_runtime_mode == "demo"
        
        # When RUNTIME_MODE changes, both default to it
        settings.RUNTIME_MODE = "live"
        assert settings.GEMINI_RUNTIME_MODE == "live"
        assert settings.PARTNER_RUNTIME_MODE == "live"
        assert settings.effective_runtime_mode == "live"
        
        # Independent override: Gemini live, Partner demo -> hybrid
        settings.RUNTIME_MODE = "demo"
        settings.GEMINI_RUNTIME_MODE = "live"
        settings.PARTNER_RUNTIME_MODE = "demo"
        assert settings.GEMINI_RUNTIME_MODE == "live"
        assert settings.PARTNER_RUNTIME_MODE == "demo"
        assert settings.effective_runtime_mode == "hybrid"
    finally:
        settings.RUNTIME_MODE = orig_rm
        settings.GEMINI_RUNTIME_MODE = orig_gm
        settings.PARTNER_RUNTIME_MODE = orig_pm


def test_health_endpoint_truthful_hybrid():
    orig_rm = settings.RUNTIME_MODE
    orig_gm = settings.GEMINI_RUNTIME_MODE
    orig_pm = settings.PARTNER_RUNTIME_MODE
    try:
        # Configure hybrid mode: Gemini live, ClickHouse demo
        settings.GEMINI_RUNTIME_MODE = "live"
        settings.PARTNER_RUNTIME_MODE = "demo"
        
        res = client.get("/api/v1/health")
        assert res.status_code == 200
        data = res.json()
        
        # Top-level truthful reporting
        assert data["runtime_mode"] == "hybrid"
        assert data["status"] == "healthy"
        
        # Independent provider evidence and modes
        gemini_info = data["providers"]["google_gemini"]
        assert gemini_info["mode"] == "live"
        assert "evidence" in gemini_info
        assert "configured" in gemini_info
        assert gemini_info["status"] in ("LIVE_CONFIGURED", "LIVE_UNCONFIGURED")
        
        ch_info = data["providers"]["clickhouse_mcp"]
        assert ch_info["mode"] == "demo"
        assert "evidence" in ch_info
        assert "configured" in ch_info
        assert ch_info["status"] == "DEMO_MODE_ACTIVE"
    finally:
        settings.RUNTIME_MODE = orig_rm
        settings.GEMINI_RUNTIME_MODE = orig_gm
        settings.PARTNER_RUNTIME_MODE = orig_pm


def test_health_endpoint_truthful_live():
    orig_rm = settings.RUNTIME_MODE
    orig_gm = settings.GEMINI_RUNTIME_MODE
    orig_pm = settings.PARTNER_RUNTIME_MODE
    try:
        # Configure fully live mode
        settings.GEMINI_RUNTIME_MODE = "live"
        settings.PARTNER_RUNTIME_MODE = "live"
        
        res = client.get("/api/v1/health")
        assert res.status_code == 200
        data = res.json()
        
        assert data["runtime_mode"] == "live"
        assert data["providers"]["google_gemini"]["mode"] == "live"
        assert data["providers"]["clickhouse_mcp"]["mode"] == "live"
    finally:
        settings.RUNTIME_MODE = orig_rm
        settings.GEMINI_RUNTIME_MODE = orig_gm
        settings.PARTNER_RUNTIME_MODE = orig_pm


@pytest.mark.asyncio
async def test_independent_fail_closed_behavior():
    orig_rm = settings.RUNTIME_MODE
    orig_gm = settings.GEMINI_RUNTIME_MODE
    orig_pm = settings.PARTNER_RUNTIME_MODE
    orig_client = gemini_service.client
    try:
        # Case: Gemini is LIVE (and unconfigured), ClickHouse is DEMO
        settings.GEMINI_RUNTIME_MODE = "live"
        settings.PARTNER_RUNTIME_MODE = "demo"
        gemini_service.client = None
        
        # Gemini service must use GEMINI_RUNTIME_MODE and fail closed
        assert gemini_service.runtime_mode == "live"
        gem_res = gemini_service.extract_continuity_tokens("Maya Vance", "Test shot prompt")
        assert gem_res["success"] is False
        assert gem_res["mode"] in ("live_unavailable", "live_error")
        
        # ClickHouse MCP must use PARTNER_RUNTIME_MODE and run in demo mode
        assert clickhouse_mcp_server.runtime_mode == "demo"
        ch_res = await clickhouse_mcp_server.call_tool("run_query", {"query": "SELECT 1"})
        assert ch_res["status"] == "success"
        assert ch_res["mode"] == "demo"
        
        # Case: Gemini is DEMO, ClickHouse is LIVE (and unconfigured)
        settings.GEMINI_RUNTIME_MODE = "demo"
        settings.PARTNER_RUNTIME_MODE = "live"
        
        assert gemini_service.runtime_mode == "demo"
        gem_res2 = gemini_service.extract_continuity_tokens("Maya Vance", "Test shot prompt")
        assert gem_res2["success"] is True
        assert gem_res2["mode"] == "demo"
        
        assert clickhouse_mcp_server.runtime_mode == "live"
        ch_res2 = await clickhouse_mcp_server.call_tool("run_query", {"query": "SELECT 1"})
        assert ch_res2["status"] == "error"
        assert ch_res2["mode"] in ("live_unavailable", "live_error")
    finally:
        settings.RUNTIME_MODE = orig_rm
        settings.GEMINI_RUNTIME_MODE = orig_gm
        settings.PARTNER_RUNTIME_MODE = orig_pm
        gemini_service.client = orig_client


@pytest.mark.asyncio
async def test_hybrid_continuity_workflow_truthful_execution():
    orig_rm = settings.RUNTIME_MODE
    orig_gm = settings.GEMINI_RUNTIME_MODE
    orig_pm = settings.PARTNER_RUNTIME_MODE
    orig_client = gemini_service.client
    try:
        # Hybrid 1: Gemini Demo (works), ClickHouse Live unconfigured (fails closed)
        settings.GEMINI_RUNTIME_MODE = "demo"
        settings.PARTNER_RUNTIME_MODE = "live"
        
        res = await continuity_agent.verify_shot_continuity("Maya Vance", "Cyber trenchcoat in rain")
        assert res["status"] == "LIVE_ERROR"
        assert res["mode"] in ("live_unavailable", "live_error")
        assert "gemini_extracted_tokens" in res  # Gemini completed successfully in demo mode
        
        # Hybrid 2: Gemini Live unconfigured (fails closed), ClickHouse Demo
        settings.GEMINI_RUNTIME_MODE = "live"
        settings.PARTNER_RUNTIME_MODE = "demo"
        gemini_service.client = None
        
        res2 = await continuity_agent.verify_shot_continuity("Maya Vance", "Cyber trenchcoat in rain")
        assert res2["status"] == "LIVE_ERROR"
        assert res2["mode"] in ("live_unavailable", "live_error")
        assert res2["clickhouse_evidence_source"] == "mcp-clickhouse (Not Reached)"
    finally:
        settings.RUNTIME_MODE = orig_rm
        settings.GEMINI_RUNTIME_MODE = orig_gm
        settings.PARTNER_RUNTIME_MODE = orig_pm
        gemini_service.client = orig_client


