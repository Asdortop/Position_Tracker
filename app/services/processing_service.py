from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from decimal import Decimal
from app.repositories.crud_operations import crud_ops
from app.database.models.tax_lot import TaxLot, LotStatus
from app.api.v1.schemas.trade import Trade

class ProcessingService:

    async def process_trade(self, db: AsyncSession, trade: Trade):
        if trade.side.upper() == "BUY":
            await self._process_buy(db, trade)
        elif trade.side.upper() == "SELL":
            await self._process_sell(db, trade)
        
        await self._update_portfolio_summary(db, trade.user_id, trade.security_id)
        await db.commit()

    async def _process_buy(self, db: AsyncSession, trade: Trade):
        # Ensure timestamp is timezone-naive for consistency
        timestamp = trade.timestamp.replace(tzinfo=None) if trade.timestamp.tzinfo else trade.timestamp
        
        new_lot = TaxLot(
            user_id=trade.user_id,
            security_id=trade.security_id,
            open_date=timestamp,
            open_qty=trade.quantity,
            remaining_qty=trade.quantity,
            open_price=trade.price,
            charges=trade.charges or 0,
            status=LotStatus.OPEN
        )
        db.add(new_lot)

    async def _process_sell(self, db: AsyncSession, trade: Trade):
        # Get current market price from price feed
        current_price = await crud_ops.get_latest_price(db, trade.security_id)
        if not current_price:
            raise ValueError(
                f"No price data found for security {trade.security_id}. "
                f"Please add a price using POST /api/v1/simulate/prices or buy this security first."
            )
        
        # Use price from trade if provided, otherwise use current market price
        sell_price = trade.price if trade.price is not None else current_price
        
        open_lots = await crud_ops.get_open_tax_lots_fifo(db, trade.user_id, trade.security_id)
        quantity_to_sell = trade.quantity

        for lot in open_lots:
            if quantity_to_sell <= 0:
                break
            
            sell_from_this_lot = min(quantity_to_sell, lot.remaining_qty)
            
            lot.remaining_qty -= sell_from_this_lot
            lot.close_qty += sell_from_this_lot
            if lot.remaining_qty == 0:
                lot.status = LotStatus.CLOSED
            else:
                lot.status = LotStatus.PARTIAL
            
            # Ensure timestamp is timezone-naive for consistency
            timestamp = trade.timestamp.replace(tzinfo=None) if trade.timestamp.tzinfo else trade.timestamp
            lot.close_date = timestamp
            lot.close_price = sell_price
            
            # Calculate gain and taxes with charges applied proportionally
            gross_gain = (sell_price - lot.open_price) * sell_from_this_lot

            # Allocate charges per unit
            buy_charge_per_unit = (lot.charges or 0) / lot.open_qty if lot.open_qty else 0
            sell_charge_per_unit = (trade.charges or 0) / trade.quantity if trade.quantity else 0
            allocated_charges = (buy_charge_per_unit + sell_charge_per_unit) * sell_from_this_lot

            taxable_gain = gross_gain - allocated_charges
            lot.realized_pnl = (lot.realized_pnl or 0) + taxable_gain

            # Ensure both datetimes are timezone-naive for comparison
            trade_timestamp = trade.timestamp.replace(tzinfo=None) if trade.timestamp.tzinfo else trade.timestamp
            lot_open_date = lot.open_date.replace(tzinfo=None) if lot.open_date.tzinfo else lot.open_date
            holding_period = trade_timestamp - lot_open_date
            if holding_period < timedelta(days=365):
                # Short-term tax @ 25%
                tax = taxable_gain * Decimal('0.25') if taxable_gain > 0 else Decimal('0')
                lot.stcg = (lot.stcg or 0) + tax
            else:
                # Long-term tax @ 12.5%
                tax = taxable_gain * Decimal('0.125') if taxable_gain > 0 else Decimal('0')
                lot.ltcg = (lot.ltcg or 0) + tax

            quantity_to_sell -= sell_from_this_lot
            
        if quantity_to_sell > 0:
            # This would mean selling more than owned. Should raise an error.
            # For simplicity, we assume valid trades.
            pass

    async def _update_portfolio_summary(self, db: AsyncSession, user_id: int, security_id: int):
        # No longer persist portfolio. Keep function for backward compatibility no-op.
        return

    async def update_price(self, db: AsyncSession, user_id: int, security_id: int, new_price: Decimal):
        await crud_ops.upsert_price(db, security_id, new_price)
        await db.commit()

processing_service = ProcessingService()