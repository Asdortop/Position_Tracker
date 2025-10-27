from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.api.v1.schemas.portfolio import PortfolioSnapshot, PortfolioSummary, PortfolioPosition
from app.core.exceptions import PortfolioNotFound
from decimal import Decimal
from app.repositories.crud_operations import crud_ops
from app.database.models.tax_lot import TaxLot, LotStatus
from sqlalchemy.future import select

class PortfolioService:
    async def get_portfolio_snapshot(self, db: AsyncSession, user_id: int) -> PortfolioSnapshot:
        """
        Generates a full portfolio snapshot for a given user.
        This method computes PnL and aggregates data based on the formulas provided.
        """
        # Compute on-the-fly from tax lots and latest price
        result = await db.execute(
            select(TaxLot.security_id, TaxLot.remaining_qty, TaxLot.open_price)
            .where(TaxLot.user_id == user_id, TaxLot.remaining_qty > 0, TaxLot.status.in_([LotStatus.OPEN, LotStatus.PARTIAL]))
        )
        rows = result.all()
        if not rows:
            raise PortfolioNotFound("No portfolio data found for this user.")

        # Aggregate by security_id
        by_sec: dict[int, dict[str, Decimal]] = {}
        for sec_id, rem_qty, open_price in rows:
            agg = by_sec.setdefault(sec_id, {"qty": Decimal(0), "cost": Decimal(0)})
            agg["qty"] += rem_qty
            agg["cost"] += rem_qty * open_price

        positions: list[PortfolioPosition] = []
        total_market_value = Decimal(0)
        total_unrealized_pnl = Decimal(0)

        for sec_id, agg in by_sec.items():
            qty = agg["qty"]
            avg_cost = (agg["cost"] / qty) if qty > 0 else Decimal(0)
            price = await crud_ops.get_latest_price(db, sec_id) or Decimal(0)
            
            # If no price data, skip this position to avoid showing $0 market value
            if price == 0:
                continue
            
            market_value = price * qty
            unreal = (price - avg_cost) * qty if qty > 0 else Decimal(0)
            positions.append(PortfolioPosition(
                security_id=str(sec_id),
                quantity=qty,
                avg_cost_basis=avg_cost,
                current_price=price,
                market_value=market_value,
                unrealized_pnl=unreal,
            ))
            total_market_value += market_value
            total_unrealized_pnl += unreal

        # Gains YTD from closed lots
        from datetime import date
        year = datetime.now().year
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        res = await db.execute(
            select(TaxLot.realized_pnl, TaxLot.stcg, TaxLot.ltcg)
            .where(
                TaxLot.user_id == user_id,
                TaxLot.close_date.isnot(None),
                TaxLot.close_date.between(start_date, end_date)
            )
        )
        rows2 = res.all()
        realized_pnl = sum((r[0] or Decimal(0)) for r in rows2) if rows2 else Decimal(0)
        st = sum((r[1] or Decimal(0)) for r in rows2) if rows2 else Decimal(0)
        lt = sum((r[2] or Decimal(0)) for r in rows2) if rows2 else Decimal(0)

        summary = PortfolioSummary(
            user_id=user_id,
            total_market_value=total_market_value,
            total_unrealized_pnl=total_unrealized_pnl,
            realized_pnl_ytd=realized_pnl,
            stcg_ytd=st,
            ltcg_ytd=lt,
            last_updated=datetime.now(),
        )

        return PortfolioSnapshot(summary=summary, positions=positions)

# Create a singleton instance
portfolio_service = PortfolioService()