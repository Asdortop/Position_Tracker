from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.database.models.portfolio import Portfolio
from app.database.models.tax_lot import TaxLot, LotStatus
from app.database.models.price import SecurityPrice
from decimal import Decimal

class CRUDOperations:
    async def get_portfolio_summary(self, db: AsyncSession, user_id: int, security_id: int):
        result = await db.execute(
            select(Portfolio).where(Portfolio.user_id == user_id, Portfolio.security_id == security_id)
        )
        return result.scalars().first()

    async def get_or_create_portfolio_summary(self, db: AsyncSession, user_id: int, security_id: int):
        summary = await self.get_portfolio_summary(db, user_id, security_id)
        if not summary:
            summary = Portfolio(
                user_id=user_id,
                security_id=security_id,
                quantity=Decimal(0),
                avg_cost_basis=Decimal(0),
                current_price=Decimal(0), # Will be updated by price feed
                unrealized_pnl=Decimal(0)
            )
            db.add(summary)
            await db.flush()
        return summary
    
    async def get_open_tax_lots_fifo(self, db: AsyncSession, user_id: int, security_id: int):
        result = await db.execute(
            select(TaxLot)
            .where(
                TaxLot.user_id == user_id,
                TaxLot.security_id == security_id,
                TaxLot.status.in_([LotStatus.OPEN, LotStatus.PARTIAL])
            )
            .order_by(TaxLot.open_date.asc())
        )
        return result.scalars().all()

    async def get_capital_gains_report(self, db: AsyncSession, user_id: int, year: int):
        """
        Generate capital gains report grouped by STCG/LTCG.
        Note: This calculates gains from stcg and ltcg fields in tax lots.
        """
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        
        # Get realized PnL grouped by whether it's short-term or long-term based on stcg/ltcg
        result = await db.execute(
            select(
                func.sum(TaxLot.realized_pnl).label('total_realized_pnl'),
                func.sum(TaxLot.stcg).label('total_stcg'),
                func.sum(TaxLot.ltcg).label('total_ltcg')
            )
            .where(
                TaxLot.user_id == user_id,
                TaxLot.status == LotStatus.CLOSED,
                TaxLot.close_date.between(start_date, end_date)
            )
        )
        return result.all()

    
    async def upsert_price(self, db: AsyncSession, security_id: int, price: Decimal):
        existing = await db.execute(select(SecurityPrice).where(SecurityPrice.security_id == security_id))
        row = existing.scalars().first()
        if row:
            row.price = price
        else:
            db.add(SecurityPrice(security_id=security_id, price=price))
        await db.flush()

    async def get_latest_price(self, db: AsyncSession, security_id: int) -> Decimal | None:
        result = await db.execute(select(SecurityPrice).where(SecurityPrice.security_id == security_id))
        row = result.scalars().first()
        return row.price if row else None

crud_ops = CRUDOperations()

