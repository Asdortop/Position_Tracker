from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime
from decimal import Decimal
from typing import Optional

class Trade(BaseModel):
    user_id: int
    security_id: int
    side: str # "BUY" or "SELL"
    quantity: Decimal
    price: Optional[Decimal] = None  # Optional - for SELL, will use current market price
    timestamp: datetime = datetime.now()
    charges: Optional[Decimal] = None
    
    @model_validator(mode='after')
    def validate_price_for_buy(self):
        """Ensure price is provided for BUY orders"""
        if self.side.upper() == "BUY" and self.price is None:
            raise ValueError("Price is required for BUY trades")
        return self
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "example": "SELL Trade (price optional - uses market price from feed)",
                    "summary": "SELL without price",
                    "value": {
                        "user_id": 1,
                        "security_id": 1,
                        "side": "SELL",
                        "quantity": 10,
                        "price": None  # Optional - will use current market price from price feed
                    }
                },
                {
                    "example": "BUY Trade (price required)",
                    "summary": "BUY with price",
                    "value": {
                        "user_id": 1,
                        "security_id": 1,
                        "side": "BUY",
                        "quantity": 10,
                        "price": 100.50,
                        "charges": 5.00
                    }
                }
            ]
        }