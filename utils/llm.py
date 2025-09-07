from __future__ import annotations

import json
import os
from typing import Dict, Any


class LLMClient:
    def __init__(self, provider: str = "heuristic", openai_api_key: str | None = None, anthropic_api_key: str | None = None) -> None:
        self.provider = provider
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")

    def _openai_chat(self, prompt: str) -> str:
        try:
            from openai import OpenAI  # type: ignore
            api_key = self.openai_api_key or os.getenv("OPENAI_API_KEY")
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return json.dumps({"error": str(e)})

    def _anthropic_chat(self, prompt: str) -> str:
        try:
            from anthropic import Anthropic  # type: ignore
            api_key = self.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
            client = Anthropic(api_key=api_key)
            msg = client.messages.create(model="claude-3-haiku-20240307", max_tokens=800, temperature=0.3, messages=[{"role": "user", "content": prompt}])
            return "".join([b.text for b in msg.content])
        except Exception as e:
            return json.dumps({"error": str(e)})

    def _heuristic(self, prompt: str) -> str:
        # very naive structured mock when no API keys are present
        fallback = {
            "sections": {
                "summary": "Clear, concise, and tailored summary recommended.",
                "experience": "Use action verbs; quantify with metrics where possible.",
                "education": "Ensure relevant coursework and honors are highlighted.",
                "skills": "Group by category and align with target role keywords.",
            },
            "scores": {"summary": 70, "experience": 75, "education": 80, "skills": 65},
            "improved_resume": "(Model output placeholder – add API key for richer suggestions)",
        }
        return json.dumps(fallback)

    def generate_structured_feedback(self, prompt: str) -> Dict[str, Any]:
        if self.provider == "openai":
            raw = self._openai_chat(prompt)
        elif self.provider == "anthropic":
            raw = self._anthropic_chat(prompt)
        else:
            raw = self._heuristic(prompt)
        try:
            return json.loads(raw)
        except Exception:
            return {"sections": {"general": raw[:2000]}}

    def generate_quantified_rewrites(self, prompt: str) -> Dict[str, Any]:
        # same JSON-mode expectations
        return self.generate_structured_feedback(prompt)



