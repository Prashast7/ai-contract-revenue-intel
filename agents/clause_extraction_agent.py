import os
import json
from typing import List
from anthropic import Anthropic
from schemas.clause_schema import Clause


class ClauseExtractionAgent:

    def __init__(self, model: str, temperature: float):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = model
        self.temperature = temperature

    def run(self, contract_text: str) -> List[Clause]:
        system_prompt = (
            "You are a legal contract analysis system. "
            "Extract enforceable clauses from the contract text. "
            "Return ONLY valid JSON array matching the schema."
        )

        user_prompt = f"""
Extract clauses of type:
- payment_term
- sla
- penalty
- renewal

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

        raw_output = response.content[0].text
        parsed = json.loads(raw_output)

        return [Clause(**item) for item in parsed]
