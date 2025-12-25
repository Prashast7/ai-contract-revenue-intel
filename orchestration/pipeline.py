from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

if not os.getenv("ANTHROPIC_API_KEY"):
    raise RuntimeError("ANTHROPIC_API_KEY not loaded")

from config.config_loader import load_config
from ingestion.contract_loader import load_contracts
from ingestion.invoice_loader import load_invoices
from agents.clause_extraction_agent import ClauseExtractionAgent
from agents.revenue_leakage_agent import RevenueLeakageAgent


def main():
    config = load_config()

    contracts = load_contracts(config.paths.contracts_dir)
    invoices = load_invoices(config.paths.invoices_dir)

    clause_agent = ClauseExtractionAgent(
        model=config.llm.extraction_model,
        temperature=config.llm.temperature.extraction,
        max_tokens=config.llm.max_tokens,
    )

    leakage_agent = RevenueLeakageAgent(
        model=config.llm.reasoning_model,
        temperature=config.llm.temperature.reasoning,
        max_tokens=config.llm.max_tokens,
    )

    for contract in contracts:
        print("\n==============================")
        print(f"Contract: {contract['contract_id']}")
        print("==============================")

        clauses = clause_agent.run(contract["text"])

        for invoice in invoices:
            findings = leakage_agent.run(
                clauses=[c.dict() for c in clauses],
                invoice=invoice,
            )

            if not findings:
                print(f"No issues for invoice {invoice['invoice_id']}")
                continue

            for finding in findings:
                print("\nREVENUE LEAKAGE FOUND")
                print(finding.dict())


if __name__ == "__main__":
    main()
