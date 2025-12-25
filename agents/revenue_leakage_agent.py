from dotenv import load_dotenv
load_dotenv()

import os
import json
import re
from typing import List
from anthropic import Anthropic
from schemas.leakage_schema import RevenueLeakage


class RevenueLeakageAgent:
    def __init__(self, model: str, temperature: float, max_tokens: int):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not loaded")

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _extract_json_array(self, text: str) -> str:
        match = re.search(r"\[\s*{[\s\S]*?}\s*\]", text)
        if not match:
            raise ValueError(f"No JSON found in response:\n{text}")
        return match.group(0)

    def run(self, clauses: List[dict], invoice: dict) -> List[RevenueLeakage]:
        system_prompt = (
            "You are a revenue assurance AI. "
            "Your task is to find missed revenue or contractual violations. "
            "Return ONLY a JSON array."
        )

        user_prompt = (
            "Contract clauses:\n"
            f"{json.dumps(clauses, indent=2)}\n\n"
            "Invoice data:\n"
            f"{json.dumps(invoice, indent=2)}\n\n"
            "Identify revenue leakage using this schema:\n"
            "{\n"
            '  "invoice_id": string,\n'
            '  "issue_type": "sla_penalty | user_overage | underbilling",\n'
            '  "estimated_amount_usd": number,\n'
            '  "confidence": "low | medium | high",\n'
            '  "recommendation": string\n'
            "}"
        )

        response = self.client.messages.create(
            model=self.model,                 # ← Claude Sonnet 4.5
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        raw_text = response.content[0].text.strip()
        parsed = json.loads(self._extract_json_array(raw_text))

        return [RevenueLeakage(**item) for item in parsed]
