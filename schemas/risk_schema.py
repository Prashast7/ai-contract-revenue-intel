from pydantic import BaseModel


class ContractRisk(BaseModel):
    contract_id: str
    risk_level: str  # low | medium | high
    key_drivers: list[str]
    mitigation_recommendations: list[str]
