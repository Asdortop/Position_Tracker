from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

class PortfolioPosition(BaseModel):
    security_id: str
    quantity: Decimal
    avg_cost_basis: Decimal
    current_price: Decimal
    market_value: Decimal
    unrealized_pnl: Decimal

    class Config:
        from_attributes = True

class PortfolioSummary(BaseModel):
    user_id: int
    total_market_value: Decimal
    total_unrealized_pnl: Decimal
    realized_pnl_ytd: Decimal
    stcg_ytd: Decimal
    ltcg_ytd: Decimal
    last_updated: datetime

class PortfolioSnapshot(BaseModel):
    summary: PortfolioSummary
    positions: list[PortfolioPosition]