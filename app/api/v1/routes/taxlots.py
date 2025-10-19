from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.v1 import dependencies
from app.models.tax_lot import TaxLot, LotStatus
from app.api.v1.schemas.tax_lot import TaxLotRead

router = APIRouter()

@router.get("/", response_model=list[TaxLotRead])
async def list_taxlots(
    user_id: int = Query(...),
    security_id: int | None = Query(None),
    status: LotStatus | None = Query(None),
    db: AsyncSession = Depends(dependencies.get_db),
):
    stmt = select(TaxLot).where(TaxLot.user_id == user_id)
    if security_id is not None:
        stmt = stmt.where(TaxLot.security_id == security_id)
    if status is not None:
        stmt = stmt.where(TaxLot.status == status)
    stmt = stmt.order_by(TaxLot.open_date.asc())
    res = await db.execute(stmt)
    return res.scalars().all()


