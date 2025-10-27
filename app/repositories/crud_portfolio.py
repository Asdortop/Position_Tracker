from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models.portfolio import Portfolio
from app.database.models.tax_lot import TaxLot, LotStatus

class CRUDPortfolio:
    async def get_portfolio_by_user(self, db: AsyncSession, user_id: int):
        result = await db.execute(select(Portfolio).where(Portfolio.user_id == user_id))
        return result.scalars().all()
    
    async def get_open_tax_lots_by_security(
        self, db: AsyncSession, user_id: int, security_id: int
    ):
        result = await db.execute(
            select(TaxLot)
            .where(
                TaxLot.user_id == user_id,
                TaxLot.security_id == security_id,
                TaxLot.remaining_qty > 0,
                TaxLot.status.in_([LotStatus.OPEN, LotStatus.PARTIAL])
            )
            .order_by(TaxLot.open_date.asc()) # Important for FIFO
        )
        return result.scalars().all()

# Create a singleton instance
crud_portfolio = CRUDPortfolio()