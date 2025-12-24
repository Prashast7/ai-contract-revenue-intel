from pydantic import BaseModel
from typing import Optional


class Clause(BaseModel):
    clause_type: str  # payment_term | sla | penalty | renewal
    description: str
    amount_or_rate: Optional[str]
    conditions: Optional[str]
    enforceable: bool
