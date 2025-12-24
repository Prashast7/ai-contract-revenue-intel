import yaml
from ingestion.contract_loader import load_contracts
from agents.clause_extraction_agent import ClauseExtractionAgent


def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()

    contracts = load_contracts(config["paths"]["contracts_dir"])

    agent = ClauseExtractionAgent(
        model=config["llm"]["model"],
        temperature=config["llm"]["temperature"],
    )

    for contract in contracts:
        clauses = agent.run(contract["text"])
        print(f"\nContract: {contract['contract_id']}")
        for clause in clauses:
            print(clause.dict())


if __name__ == "__main__":
    main()
