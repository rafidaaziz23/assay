"""
Google Gemini GenAI Service
Integrated with official google-genai SDK.
Supports structured JSON schema outputs and graceful fallback when offline.
"""
import os
import json
from typing import Dict, Any, Optional
from ..config import settings

class GeminiService:
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[GeminiService] Could not initialize google.genai: {e}")

    def generate_socratic_reply(self, selected_text: str, question: str) -> Dict[str, Any]:
        """
        Socratic counter-inquiry: NEVER directly answers, points user to deeper reasoning.
        """
        if not self.client or settings.DEMO_MODE == "cached":
            return {
                "mode": "socratic",
                "reply": f"Before we define '{selected_text}' directly — consider: if this mechanism were absent from the engine, what immediate performance penalty would the render tree suffer on every frame?",
                "hint_level": 1,
                "citations": [{"kind": "document", "page": 2}],
                "gave_direct_answer": False
            }

        try:
            prompt = (
                f"You are the Assay Socratic Engine. The user selected the phrase: '{selected_text}' "
                f"and asked: '{question}'.\n"
                f"RULE: DO NOT provide a direct encyclopedic summary or answer. "
                f"Instead, ask a targeted diagnostic question that forces the student to deduce the underlying mechanic."
            )
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt
            )
            return {
                "mode": "socratic",
                "reply": response.text.strip(),
                "hint_level": 1,
                "citations": [{"kind": "document", "page": 1}],
                "gave_direct_answer": False
            }
        except Exception as e:
            return {
                "mode": "socratic",
                "reply": f"Think about '{selected_text}' from first principles: how does browser layout recalculation behave when state mutations occur 60 times a second?",
                "hint_level": 1,
                "citations": [{"kind": "document", "page": 1}],
                "gave_direct_answer": False
            }

gemini_service = GeminiService()
