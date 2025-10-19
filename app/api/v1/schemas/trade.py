from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class Trade(BaseModel):
    user_id: int
    security_id: int
    side: str # "BUY" or "SELL"
    quantity: Decimal
    price: Decimal
    timestamp: datetime = datetime.now()
    charges: Decimal | None = 0