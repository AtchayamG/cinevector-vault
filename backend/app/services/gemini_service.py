import os
import json
import logging
import time
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger("cinevector.gemini")

class GeminiService:
    """
    Google GenAI SDK & Gemini 3.7 Flash Integration Service for CineVector Vault.
    Analyzes scene visual prompts and extracts structured visual continuity tokens
    (costume items, lighting palettes, facial features, props) for vector embedding and ClickHouse matching.
    """
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.project = settings.GOOGLE_CLOUD_PROJECT
        self.location = settings.GOOGLE_CLOUD_LOCATION
        self.model_name = settings.GEMINI_MODEL
        self._runtime_mode: Optional[str] = None
        self.client = None
        self._init_client()

    @property
    def runtime_mode(self) -> str:
        if self._runtime_mode is not None:
            return self._runtime_mode
        return settings.GEMINI_RUNTIME_MODE

    @runtime_mode.setter
    def runtime_mode(self, value: Optional[str]):
        if value is None or value.lower() == settings.GEMINI_RUNTIME_MODE.lower():
            self._runtime_mode = None
        else:
            self._runtime_mode = value.lower()

    def _init_client(self):
        if self.api_key or (self.project and self.location) or os.getenv("K_SERVICE") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            try:
                from google import genai
                if self.api_key:
                    self.client = genai.Client(api_key=self.api_key)
                elif self.project:
                    self.client = genai.Client(vertexai=True, project=self.project, location=self.location or "global")
                else:
                    self.client = genai.Client(vertexai=True, location=self.location or "global")
                logger.info(f"Initialized Google GenAI Client with model: {self.model_name} (Mode: LIVE)")
            except Exception as e:
                logger.warning(f"Could not initialize google-genai client ({e}).")
                self.client = None
        else:
            logger.info("No Gemini credentials found.")

    def extract_continuity_tokens(self, character: str, shot_description: str) -> Dict[str, Any]:
        """
        Calls Gemini 3.7 Flash to extract structured visual continuity attributes.
        In live mode, returns live_error / live_unavailable on failure without falling back to demo.
        In demo mode, derives dynamic tokens from input description.
        """
        start_time = time.time()
        
        if self.runtime_mode == "live":
            if not self.client:
                return {
                    "success": False,
                    "mode": "live_unavailable",
                    "error": "Gemini API credentials (GEMINI_API_KEY, GOOGLE_CLOUD_PROJECT, or Cloud Run ADC) not configured in environment",
                    "evidence_source": "Google GenAI API (Unconfigured)",
                    "data": None
                }
            try:
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
                    "evidence_source": f"Google GenAI API ({self.model_name} Live)",
                    "data": result,
                    "latency_ms": latency_ms
                }
            except Exception as e:
                logger.error(f"Gemini live continuity extraction failed: {e}")
                return {
                    "success": False,
                    "mode": "live_error",
                    "error": str(e),
                    "evidence_source": "Google GenAI API (Live Error)",
                    "data": None
                }

        # Deterministic Demo Mode with input-dependent token extraction
        latency_ms = max(int((time.time() - start_time) * 1000), 22)
        desc_lower = shot_description.lower()
        
        costume_items = []
        if "trenchcoat" in desc_lower or "coat" in desc_lower or "jacket" in desc_lower:
            costume_items.append("Charcoal cybernetic trenchcoat")
            costume_items.append("High matte collar")
        elif "lab coat" in desc_lower or "suit" in desc_lower:
            costume_items.append("White biometric lab coat")
            costume_items.append("Silver trim collar")
        else:
            costume_items.append(f"Custom attire for {character}")

        if "rain" in desc_lower or "wet" in desc_lower:
            costume_items.append("Rain droplets on fabric")

        lighting_items = []
        if "cyan" in desc_lower or "blue" in desc_lower:
            lighting_items.append("Cyan key light")
        if "magenta" in desc_lower or "red" in desc_lower or "crimson" in desc_lower:
            lighting_items.append("Magenta/Crimson rim flare")
        if not lighting_items:
            lighting_items = ["High-contrast directional lighting", "Ambient filmic fill"]

        demo_tokens = {
            "character": character,
            "costume_tokens": costume_items,
            "lighting_palette": lighting_items,
            "facial_features": [f"Determined expression for {character}"],
            "props_and_accessories": ["Holographic scanner"] if "holo" in desc_lower or "scanner" in desc_lower else ["Tactical prop"],
            "camera_framing": "35mm Anamorphic Shot",
            "visual_style": "High-contrast cinematic lighting"
        }

        return {
            "success": True,
            "mode": "demo",
            "evidence_source": "Local Visual Token Fixture (Demo Mode)",
            "data": demo_tokens,
            "latency_ms": latency_ms
        }

gemini_service = GeminiService()
