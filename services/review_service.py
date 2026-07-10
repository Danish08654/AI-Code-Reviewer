import os
import json
import re
from services.llm_service import LLMService


class ReviewService:

    def __init__(self):
        self.llm = LLMService()
        self.prompt_template = self.load_prompt()

    def load_prompt(self):
        path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "prompts",
            "review_prompt.txt"
        )

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    # =========================
    # SINGLE ROBUST PARSER
    # =========================
    def parse_json(self, text: str):

        try:
            if not text:
                return None

            text = text.strip()

            # remove markdown
            text = re.sub(r"```json|```", "", text)

            # extract JSON safely
            start = text.find("{")
            end = text.rfind("}")

            if start == -1 or end == -1:
                return None

            json_str = text[start:end + 1]

            return json.loads(json_str)

        except Exception:
            return None

    # =========================
    # NORMALIZER
    # =========================
    def normalize(self, data):

        if not isinstance(data, dict):
            return {
                "summary": "Invalid response",
                "critical_issues": [],
                "medium_issues": [],
                "suggestions": [],
                "verdict": "ERROR"
            }

        return {
            "summary": data.get("summary", ""),
            "critical_issues": data.get("critical_issues", []),
            "medium_issues": data.get("medium_issues", []),
            "suggestions": data.get("suggestions", []),
            "verdict": data.get("verdict", "NEEDS_CHANGES")
        }

    # =========================
    # MAIN FUNCTION
    # =========================
    def review_code(self, code: str):

        if not code.strip():
            return {
                "files_reviewed": 0,
                "review": self.normalize({
                    "summary": "No code provided",
                    "critical_issues": [],
                    "medium_issues": [],
                    "suggestions": [],
                    "verdict": "APPROVE"
                })
            }

        prompt = f"""
{self.prompt_template}

Return ONLY valid JSON:

{{
  "summary": "string",
  "critical_issues": ["string"],
  "medium_issues": ["string"],
  "suggestions": ["string"],
  "verdict": "APPROVE | REJECT | NEEDS_CHANGES"
}}

CODE:
{code}
"""

        raw = self.llm.generate(prompt)

        parsed = self.parse_json(raw)

        if not parsed:
            parsed = {
                "summary": "Failed to parse LLM response",
                "critical_issues": [],
                "medium_issues": [],
                "suggestions": [],
                "verdict": "ERROR"
            }

        return {
            "files_reviewed": 1,
            "review": self.normalize(parsed)
        }