import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger("cinevector.gemini")

class GeminiService:
    """
    Google GenAI SDK & Gemini 2.0 Integration Service for CineVector Vault.
    Analyzes scene visual prompts and extracts structured visual continuity tokens
    (costume items, lighting palettes, facial features, props) for vector embedding and ClickHouse matching.
    """
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.project = settings.GOOGLE_CLOUD_PROJECT
        self.location = settings.GOOGLE_CLOUD_LOCATION
        self.model_name = settings.GEMINI_MODEL
        self.runtime_mode = settings.RUNTIME_MODE
        self.client = None
        self._init_client()

    def _init_client(self):
        if self.api_key or (self.project and self.location):
            try:
                from google import genai
                if self.api_key:
                    self.client = genai.Client(api_key=self.api_key)
                else:
                    self.client = genai.Client(vertexai=True, project=self.project, location=self.location)
                logger.info(f"Initialized Google GenAI Client with model: {self.model_name} (Mode: LIVE)")
            except Exception as e:
                logger.warning(f"Could not initialize google-genai client ({e}). Running in demo mode.")
        else:
            logger.info("No Gemini credentials found. Running in deterministic DEMO fixture mode.")

    def extract_continuity_tokens(self, character: str, shot_description: str) -> Dict[str, Any]:
        """
        Calls Gemini 2.0 to extract structured visual continuity attributes.
        """
        start_time = time.time()
        prompt = f"""
        Analyze this film scene shot for character '{character}' and extract structured visual continuity parameters:
        Shot Description: {shot_description}

        Output JSON strictly matching this schema:
        {{
            "character": "{character}",
            "costume_tokens": ["string", "string"],
            "lighting_palette": ["string", "string"],
            "facial_features": ["string"],
            "props_and_accessories": ["string"],
            "camera_framing": "string",
            "visual_style": "string"
        }}
        """

        if self.client and self.runtime_mode == "live":
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config={
                        "system_instruction": "You are a Hollywood script supervisor and visual continuity inspector.",
                        "response_mime_type": "application/json"
                    }
                )
                result = json.loads(response.text.strip())
                latency_ms = int((time.time() - start_time) * 1000)
                return {
                    "success": True,
                    "mode": "live",
                    "evidence_source": "Google GenAI API (Gemini 2.0 Flash Live)",
                    "data": result,
                    "latency_ms": latency_ms
                }
            except Exception as e:
                logger.error(f"Gemini live continuity extraction failed: {e}")
                if not settings.ENABLE_MOCK_FALLBACK:
                    return {
                        "success": False,
                        "mode": "live_error",
                        "error": str(e),
                        "data": None
                    }

        # Deterministic Demo Mode
        latency_ms = max(int((time.time() - start_time) * 1000), 22)
        demo_tokens = {
            "character": character,
            "costume_tokens": ["Charcoal cybernetic trenchcoat", "High matte collar", "Reinforced shoulder plating"],
            "lighting_palette": ["Cyan anamorphic key light", "Magenta rim flare", "Wet asphalt reflections"],
            "facial_features": ["Subtle cybernetic left ocular seam", "Determined expression", "Rain-streaked cheek"],
            "props_and_accessories": ["Holographic neural scanner in right holster"],
            "camera_framing": "Medium Over-the-Shoulder, 35mm Anamorphic",
            "visual_style": "High-contrast cyberpunk noir"
        }

        return {
            "success": True,
            "mode": "demo",
            "evidence_source": "Deterministic Local Visual Token Dataset (demo fixture)",
            "data": demo_tokens,
            "latency_ms": latency_ms
        }

gemini_service = GeminiService()
