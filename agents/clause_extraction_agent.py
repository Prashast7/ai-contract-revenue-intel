from dotenv import load_dotenv
load_dotenv()

import os
import json
import re
from typing import List
from anthropic import Anthropic
from schemas.clause_schema import Clause


class ClauseExtractionAgent:
    def __init__(self, model: str, temperature: float, max_tokens: int):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not loaded")

        self.client = Anthropic(api_key=api_key)
        self.model = model                    # claude-haiku-4-5
        self.temperature = temperature        # config.llm.temperature.extraction
        self.max_tokens = max_tokens           # config.llm.max_tokens

    def _extract_json_array(self, text: str) -> str:
        """
        Extract the first JSON array from LLM output.
        """
        match = re.search(r"\[\s*{[\s\S]*?}\s*\]", text)
        if not match:
            raise ValueError(
                "Claude response did not contain a JSON array.\n"
                f"Raw response:\n{text}"
            )
        return match.group(0)

    def run(self, contract_text: str) -> List[Clause]:
        system_prompt = (
            "You are a legal contract analysis engine. "
            "Return ONLY a JSON array. No explanations. No markdown."
        )

        user_prompt = (
            "Extract enforceable clauses of the following types ONLY:\n"
            "- payment_term\n"
            "- sla\n"
            "- penalty\n"
            "- renewal\n\n"
            "Each clause must follow this schema:\n"
            "{\n"
            '  "clause_type": "payment_term | sla | penalty | renewal",\n'
            '  "description": string,\n'
            '  "amount_or_rate": string | null,\n'
            '  "conditions": string | null,\n'
            '  "enforceable": boolean\n'
            "}\n\n"
            "Contract text:\n"
            f"{contract_text}"
        )

        response = self.client.messages.create(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        raw_text = response.content[0].text.strip()
        parsed = json.loads(self._extract_json_array(raw_text))

        return [Clause(**item) for item in parsed]
