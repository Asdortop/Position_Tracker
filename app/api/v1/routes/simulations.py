from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1 import dependencies
from app.services.processing_service import processing_service
from app.api.v1.schemas.trade import Trade
from decimal import Decimal

router = APIRouter()

@router.post("/trades", status_code=202)
async def simulate_trade_event(
    trade: Trade,
    db: AsyncSession = Depends(dependencies.get_db)
):
    """
    FAKED ENDPOINT: Simulates receiving a trade from a broker/cash tracker.
    This triggers the core FIFO and P&L logic.
    """
    await processing_service.process_trade(db, trade)
    return {"message": "Trade accepted for processing."}

@router.post("/prices", status_code=200)
async def simulate_price_update(
    user_id: int = Body(...),
    security_id: int = Body(...),
    price: Decimal = Body(...),
    db: AsyncSession = Depends(dependencies.get_db)
):
    """
    FAKED ENDPOINT: Simulates receiving a price update from a price feed.
    This updates the unrealized P&L.
    """
    await processing_service.update_price(db, user_id, security_id, price)
    return {"message": f"Price for {security_id} updated to {price}."}

@router.post("/eod-taxes", status_code=200)
async def simulate_eod_taxes(
    user_id: int = Body(...),
    db: AsyncSession = Depends(dependencies.get_db)
):
    """
    Simulates end-of-day tax finalization. In this simplified version, taxes
    are already computed at trade time, so this endpoint is a no-op placeholder
    to align with an EOD batch design. Returns the day's closed lots for audit.
    """
    from sqlalchemy.future import select
    from datetime import date
    from app.models.tax_lot import TaxLot

    today = date.today().isoformat()
    res = await db.execute(
        select(TaxLot).where(TaxLot.user_id == user_id, TaxLot.close_date >= today)
    )
    return {"closed_lots_today": len(res.scalars().all())}