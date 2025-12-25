from dotenv import load_dotenv
load_dotenv()

import os
from anthropic import Anthropic


class ExecutiveSummaryAgent:
    def __init__(self, model: str, temperature: float, max_tokens: int):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not loaded")

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def run(self, contract_id: str, leakages: list[dict], risk: dict) -> str:
        system_prompt = (
            "You are a CFO advisory AI. "
            "Write concise, executive-ready summaries. No technical language."
        )

        user_prompt = (
            f"Contract ID: {contract_id}\n\n"
            f"Revenue Leakages:\n{leakages}\n\n"
            f"Risk Assessment:\n{risk}\n\n"
            "Write a one-page executive summary covering:\n"
            "- Financial exposure\n"
            "- Contract risk\n"
            "- Recommended actions"
        )

        response = self.client.messages.create(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        return response.content[0].text.strip()
