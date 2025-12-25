from dotenv import load_dotenv
from pathlib import Path
import os

# --------------------------------------------------
# ENV SETUP
# --------------------------------------------------
load_dotenv()

if not os.getenv("ANTHROPIC_API_KEY"):
    raise RuntimeError("ANTHROPIC_API_KEY not loaded")

# --------------------------------------------------
# CONFIG + LOADERS
# --------------------------------------------------
from config.config_loader import load_config
from ingestion.contract_loader import load_contracts
from ingestion.invoice_loader import load_invoices

# --------------------------------------------------
# AGENTS
# --------------------------------------------------
from agents.clause_extraction_agent import ClauseExtractionAgent
from agents.revenue_leakage_agent import RevenueLeakageAgent
from agents.risk_classification_agent import RiskClassificationAgent
from agents.executive_summary_agent import ExecutiveSummaryAgent

# --------------------------------------------------
# OUTPUT
# --------------------------------------------------
from orchestration.output_writer import write_json, write_text


def main():
    # -----------------------------
    # LOAD CONFIG
    # -----------------------------
    config = load_config()

    # -----------------------------
    # LOAD DATA
    # -----------------------------
    contracts = load_contracts(config.paths.contracts_dir)
    invoices = load_invoices(config.paths.invoices_dir)

    # -----------------------------
    # INIT AGENTS
    # -----------------------------
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

    risk_agent = RiskClassificationAgent(
        model=config.llm.reasoning_model,
        temperature=config.llm.temperature.reasoning,
        max_tokens=config.llm.max_tokens,
    )

    summary_agent = ExecutiveSummaryAgent(
        model=config.llm.reasoning_model,
        temperature=0.3,
        max_tokens=1500,
    )

    # -----------------------------
    # PIPELINE EXECUTION
    # -----------------------------
    all_results = []

    for contract in contracts:
        print("\n==============================")
        print(f"Contract: {contract['contract_id']}")
        print("==============================")

        clauses = clause_agent.run(contract["text"])
        contract_leakages = []

        for invoice in invoices:
            findings = leakage_agent.run(
                clauses=[c.dict() for c in clauses],
                invoice=invoice,
            )

            for f in findings:
                print("\nREVENUE LEAKAGE FOUND")
                print(f.dict())
                contract_leakages.append(f.dict())

        # -----------------------------
        # RISK CLASSIFICATION
        # -----------------------------
        risk = risk_agent.run(
            contract_id=contract["contract_id"],
            clauses=[c.dict() for c in clauses],
            leakages=contract_leakages,
        )

        # -----------------------------
        # EXECUTIVE SUMMARY
        # -----------------------------
        summary = summary_agent.run(
            contract_id=contract["contract_id"],
            leakages=contract_leakages,
            risk=risk.dict(),
        )

        print("\nEXECUTIVE SUMMARY")
        print("-----------------")
        print(summary)

        all_results.append(
            {
                "contract_id": contract["contract_id"],
                "leakages": contract_leakages,
                "risk": risk.dict(),
                "executive_summary": summary,
            }
        )

    # -----------------------------
    # WRITE OUTPUTS (DEMO MODE)
    # -----------------------------
    output_dir = Path(config.paths.output_dir)

    write_json(output_dir / "findings.json", all_results)
    write_text(output_dir / "executive_summary.txt", all_results[-1]["executive_summary"])


if __name__ == "__main__":
    main()
