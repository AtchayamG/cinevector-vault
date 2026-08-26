import os
import logging
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.routes.vault_routes import router as vault_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s")
logger = logging.getLogger("cinevector.main")

app = FastAPI(
    title="CineVector Vault API",
    version="1.0.0",
    description="Columnar Video Intelligence & Vector Continuity Media Lake powered by official mcp-clickhouse and Gemini 3.7 Flash."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vault_router, prefix=settings.API_PREFIX)

# Static UI directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.get("/")
@app.get("/ui")
async def serve_ui():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "service": settings.PROJECT_NAME,
        "track": settings.TRACK,
        "mode": settings.effective_runtime_mode,
        "status": "healthy",
        "docs": "/docs"
    }

@app.get("/api/v1/health")
async def health_check():
    gemini_mode = settings.GEMINI_RUNTIME_MODE
    partner_mode = settings.PARTNER_RUNTIME_MODE
    effective_mode = settings.effective_runtime_mode

    gemini_evidence = "Gemini API credentials unconfigured"
    if settings.GEMINI_API_KEY:
        gemini_evidence = "Gemini API key configured"
    elif settings.GOOGLE_CLOUD_PROJECT:
        gemini_evidence = f"Vertex AI configured (Project: {settings.GOOGLE_CLOUD_PROJECT}, Location: {settings.GOOGLE_CLOUD_LOCATION})"
    elif os.getenv("K_SERVICE"):
        gemini_evidence = "Cloud Run ADC runtime environment active"
    elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        gemini_evidence = "Application Default Credentials (ADC) file configured"

    clickhouse_configured = settings.is_clickhouse_configured
    clickhouse_evidence = (
        f"ClickHouse Cloud configured ({settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT})"
        if clickhouse_configured
        else "ClickHouse credentials unconfigured (local MergeTree fixture active)"
    )

    gemini_status = (
        "LIVE_CONFIGURED"
        if (gemini_mode == "live" and settings.is_gemini_configured)
        else ("LIVE_UNCONFIGURED" if gemini_mode == "live" else "DEMO_MODE_ACTIVE")
    )
    clickhouse_status = (
        "LIVE_CONFIGURED"
        if (partner_mode == "live" and clickhouse_configured)
        else ("LIVE_UNCONFIGURED" if partner_mode == "live" else "DEMO_MODE_ACTIVE")
    )

    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "track": settings.TRACK,
        "runtime_mode": effective_mode,
        "providers": {
            "google_gemini": {
                "mode": gemini_mode,
                "configured": settings.is_gemini_configured,
                "model": settings.GEMINI_MODEL,
                "status": gemini_status,
                "evidence": gemini_evidence
            },
            "clickhouse_mcp": {
                "mode": partner_mode,
                "configured": clickhouse_configured,
                "server": "mcp-clickhouse",
                "status": clickhouse_status,
                "evidence": clickhouse_evidence
            }
        }
    }
