"""
Price management service for the Position Tracker API.
"""
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import AsyncSessionLocal
from app.repositories.crud_operations import crud_ops


class PriceService:
    """Service for managing security prices."""
    
    @staticmethod
    async def get_current_price(security_id: int) -> Optional[Decimal]:
        """
        Get the current price for a security.
        
        Args:
            security_id: The security ID
            
        Returns:
            Current price or None if not found
        """
        async with AsyncSessionLocal() as db:
            return await crud_ops.get_latest_price(db, security_id)
    
    @staticmethod
    async def update_price(
        security_id: int,
        price: Decimal,
        db: AsyncSession
    ) -> bool:
        """
        Update the price for a security.
        
        Args:
            security_id: The security ID
            price: The new price
            db: Database session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await crud_ops.upsert_price(db, security_id, price)
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False
    
    @staticmethod
    def validate_price(price: Decimal) -> bool:
        """
        Validate that a price is reasonable.
        
        Args:
            price: The price to validate
            
        Returns:
            True if valid, False otherwise
        """
        return price > 0 and price < Decimal("1000000")  # Reasonable upper limit
