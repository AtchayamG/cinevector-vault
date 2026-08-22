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
        "mode": settings.RUNTIME_MODE,
        "status": "healthy",
        "docs": "/docs"
    }

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "track": settings.TRACK,
        "runtime_mode": settings.RUNTIME_MODE,
        "providers": {
            "google_gemini": {
                "configured": settings.is_gemini_configured,
                "model": settings.GEMINI_MODEL
            },
            "clickhouse_mcp": {
                "configured": settings.is_clickhouse_configured,
                "server": "mcp-clickhouse",
                "status": "LIVE_CONFIGURED" if settings.is_clickhouse_configured else "DEMO_MODE_ACTIVE"
            }
        }
    }
