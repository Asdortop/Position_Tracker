"""
Price update schema
"""
from pydantic import BaseModel
from decimal import Decimal


class PriceUpdate(BaseModel):
    """Schema for price update requests"""
    security_id: int
    price: Decimal
