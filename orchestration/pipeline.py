from dotenv import load_dotenv
from pathlib import Path
import os
import yaml

# --------------------------------------------------
# FORCE LOAD .env FROM PROJECT ROOT
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

if not os.getenv("ANTHROPIC_API_KEY"):
    raise RuntimeError("ANTHROPIC_API_KEY not loaded from .env")

# --------------------------------------------------
# DAY 1 IMPORTS ONLY
# --------------------------------------------------
from ingestion.contract_loader import load_contracts
from agents.clause_extraction_agent import ClauseExtractionAgent


def load_config():
    with open(PROJECT_ROOT / "config" / "config.yaml", "r") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()

    # -----------------------------
    # LOAD CONTRACTS
    # -----------------------------
    contracts = load_contracts(config["paths"]["contracts_dir"])

    # -----------------------------
    # INIT CLAUSE EXTRACTION AGENT
    # -----------------------------
    clause_agent = ClauseExtractionAgent(
        model=config["llm"]["model"],
        temperature=config["llm"]["temperature"],
    )

    # -----------------------------
    # RUN DAY 1 PIPELINE
    # -----------------------------
    for contract in contracts:
        print("\n==============================")
        print(f"Contract: {contract['contract_id']}")
        print("==============================")

        clauses = clause_agent.run(contract["text"])

        for clause in clauses:
            print(clause.model_dump())



if __name__ == "__main__":
    main()
