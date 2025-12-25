from dotenv import load_dotenv
load_dotenv()

import os
import json
import re
from anthropic import Anthropic
from schemas.risk_schema import ContractRisk


class RiskClassificationAgent:
    def __init__(self, model: str, temperature: float, max_tokens: int):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not loaded")

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _extract_json(self, text: str) -> dict:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError(f"No JSON found:\n{text}")
        return json.loads(match.group(0))

    def run(self, contract_id: str, clauses: list[dict], leakages: list[dict]) -> ContractRisk:
        system_prompt = (
            "You are a contract risk assessment AI for enterprise SaaS agreements. "
            "Return ONLY valid JSON."
        )

        user_prompt = (
            f"Contract ID: {contract_id}\n\n"
            f"Clauses:\n{json.dumps(clauses, indent=2)}\n\n"
            f"Revenue Leakages:\n{json.dumps(leakages, indent=2)}\n\n"
            "Classify overall contract risk using this schema:\n"
            "{\n"
            '  "contract_id": string,\n'
            '  "risk_level": "low | medium | high",\n'
            '  "key_drivers": [string],\n'
            '  "mitigation_recommendations": [string]\n'
            "}"
        )

        response = self.client.messages.create(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        return ContractRisk(**self._extract_json(response.content[0].text))
