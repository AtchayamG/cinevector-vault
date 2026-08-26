import os
from typing import List, Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "CineVector Vault"
    TRACK: str = "ClickHouse Partner Track"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Runtime Mode: 'live' or 'demo'
    RUNTIME_MODE: str = os.getenv("RUNTIME_MODE", "demo").lower()
    _gemini_runtime_mode: Optional[str] = None
    _partner_runtime_mode: Optional[str] = None

    def __init__(self, **values):
        super().__init__(**values)
        if "GEMINI_RUNTIME_MODE" in values and values["GEMINI_RUNTIME_MODE"] is not None:
            self._gemini_runtime_mode = str(values["GEMINI_RUNTIME_MODE"]).lower()
        if "PARTNER_RUNTIME_MODE" in values and values["PARTNER_RUNTIME_MODE"] is not None:
            self._partner_runtime_mode = str(values["PARTNER_RUNTIME_MODE"]).lower()

    @property
    def GEMINI_RUNTIME_MODE(self) -> str:
        if self._gemini_runtime_mode is not None:
            return self._gemini_runtime_mode
        env_val = os.getenv("GEMINI_RUNTIME_MODE")
        if env_val:
            return env_val.lower()
        return self.RUNTIME_MODE.lower()

    @GEMINI_RUNTIME_MODE.setter
    def GEMINI_RUNTIME_MODE(self, val: Optional[str]):
        self._gemini_runtime_mode = val.lower() if val is not None else None

    @property
    def PARTNER_RUNTIME_MODE(self) -> str:
        if self._partner_runtime_mode is not None:
            return self._partner_runtime_mode
        env_val = os.getenv("PARTNER_RUNTIME_MODE")
        if env_val:
            return env_val.lower()
        return self.RUNTIME_MODE.lower()

    @PARTNER_RUNTIME_MODE.setter
    def PARTNER_RUNTIME_MODE(self, val: Optional[str]):
        self._partner_runtime_mode = val.lower() if val is not None else None

    @property
    def effective_runtime_mode(self) -> str:
        g = self.GEMINI_RUNTIME_MODE
        p = self.PARTNER_RUNTIME_MODE
        if g == p:
            return g
        return "hybrid"
    
    # Google Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    GOOGLE_CLOUD_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
    
    # Server
    PORT: int = int(os.getenv("PORT", 8001))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    CORS_ORIGINS: List[str] = ["*"]
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    ENABLE_MOCK_FALLBACK: bool = os.getenv("ENABLE_MOCK_FALLBACK", "false").lower() in ("true", "1", "yes")
    
    # ClickHouse Cloud / MCP Server
    CLICKHOUSE_HOST: str = os.getenv("CLICKHOUSE_HOST", "localhost")
    CLICKHOUSE_PORT: int = int(os.getenv("CLICKHOUSE_PORT", 8443))
    CLICKHOUSE_USER: str = os.getenv("CLICKHOUSE_USER", "default")
    CLICKHOUSE_PASSWORD: str = os.getenv("CLICKHOUSE_PASSWORD", "")
    CLICKHOUSE_DATABASE: str = os.getenv("CLICKHOUSE_DATABASE", "cinevector_vault")
    CLICKHOUSE_SECURE: bool = os.getenv("CLICKHOUSE_SECURE", "true").lower() in ("true", "1", "yes")
    CLICKHOUSE_MCP_ENDPOINT: str = os.getenv("CLICKHOUSE_MCP_ENDPOINT", "http://localhost:8010/mcp")

    @property
    def is_gemini_configured(self) -> bool:
        return bool(
            self.GEMINI_API_KEY
            or (self.GOOGLE_CLOUD_PROJECT and self.GOOGLE_CLOUD_LOCATION)
            or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            or os.getenv("K_SERVICE")
        )

    @property
    def is_clickhouse_configured(self) -> bool:
        return bool(self.CLICKHOUSE_PASSWORD and self.CLICKHOUSE_HOST and self.CLICKHOUSE_HOST != "localhost")

settings = Settings()
