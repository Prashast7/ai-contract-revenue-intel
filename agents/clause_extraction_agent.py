
### Replace the ENTIRE file with this:


from dotenv import load_dotenv
load_dotenv()

import os
import json
import re
from typing import List
from anthropic import Anthropic
from schemas.clause_schema import Clause


class ClauseExtractionAgent:
    def __init__(self, model: str, temperature: float):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not loaded")

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def _extract_json(self, text: str) -> str:
        """
        Extract JSON array from LLM output.
        """
        match = re.search(r"\[\s*{.*}\s*\]", text, re.DOTALL)
        if not match:
            raise ValueError(f"LLM did not return JSON:\n{text}")

        return match.group(0)

    def run(self, contract_text: str) -> List[Clause]:
        system_prompt = (
            "You are a legal contract analysis engine. "
            "Return ONLY a JSON array. No explanations. No markdown."
        )

        user_prompt = f"""
Extract enforceable clauses of these types ONLY:
- payment_term
- sla
- penalty
- renewal

Each clause must follow this schema:
{{
  "clause_type": "payment_term | sla | penalty | renewal",
  "description": string,
  "amount_or_rate": string | null,
  "conditions": string | null,
  "enforceable": boolean
}}

Contract text:
{contract_text}
"""

        response = self.client.messages.create(
            model=self.model,
            temperature=self.temperature,
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        raw_text = response.content[0].text.strip()

        json_text = self._extract_json(raw_text)
        parsed = json.loads(json_text)

        return [Clause(**item) for item in parsed]
