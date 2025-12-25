from pydantic import BaseModel


class RevenueLeakage(BaseModel):
    invoice_id: str
    issue_type: str  # sla_penalty | user_overage | underbilling
    estimated_amount_usd: float
    confidence: str  # low | medium | high
    recommendation: str
