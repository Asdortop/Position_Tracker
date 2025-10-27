from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from app.database.models.tax_lot import LotStatus

class TaxLotBase(BaseModel):
    user_id: int
    security_id: int
    open_date: datetime
    open_qty: Decimal
    open_price: Decimal

class TaxLotRead(TaxLotBase):
    id: int
    remaining_qty: Decimal
    close_qty: Decimal
    status: LotStatus
    close_date: datetime | None = None
    close_price: Decimal | None = None
    charges: Decimal
    realized_pnl: Decimal
    stcg: Decimal
    ltcg: Decimal

    class Config:
        from_attributes = True