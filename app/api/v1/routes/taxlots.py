from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.v1 import dependencies
from app.database.models.tax_lot import TaxLot, LotStatus
from app.api.v1.schemas.tax_lot import TaxLotRead
from pydantic import BaseModel
from typing import List

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


# Event Master Integration Schema
class EventMasterResponse(BaseModel):
    user_id: int
    security_id: int
    open_qty: float
    remaining_qty: float
    open_price: float
    open_date: str
    status: str

class EventMasterSecurityResponse(BaseModel):
    security_id: int
    total_open_lots: int
    total_remaining_qty: float
    total_users_affected: int
    lots: List[EventMasterResponse]

@router.get("/event-master/{security_id}", response_model=EventMasterSecurityResponse)
async def get_security_lots_for_event(
    security_id: int,
    db: AsyncSession = Depends(dependencies.get_db),
):
    """
    Event Master Integration Endpoint
    
    When an event occurs for a specific security, this endpoint retrieves
    all open and partial lots for that security across all users.
    
    Returns:
    - security_id: The security that triggered the event
    - total_open_lots: Number of open/partial lots
    - total_remaining_qty: Total remaining quantity across all lots
    - total_users_affected: Number of unique users with open positions
    - lots: List of individual lot details
    """
    
    # Query all open and partial lots for this security
    stmt = select(TaxLot).where(
        TaxLot.security_id == security_id,
        TaxLot.status.in_([LotStatus.OPEN, LotStatus.PARTIAL]),
        TaxLot.remaining_qty > 0
    ).order_by(TaxLot.open_date.asc())
    
    result = await db.execute(stmt)
    lots = result.scalars().all()
    
    if not lots:
        raise HTTPException(
            status_code=404, 
            detail=f"No open or partial lots found for security_id: {security_id}"
        )
    
    # Process the data
    lots_data = []
    total_remaining_qty = 0
    unique_users = set()
    
    for lot in lots:
        lots_data.append(EventMasterResponse(
            user_id=lot.user_id,
            security_id=lot.security_id,
            open_qty=float(lot.open_qty),
            remaining_qty=float(lot.remaining_qty),
            open_price=float(lot.open_price),
            open_date=lot.open_date.isoformat(),
            status=lot.status.value
        ))
        
        total_remaining_qty += float(lot.remaining_qty)
        unique_users.add(lot.user_id)
    
    return EventMasterSecurityResponse(
        security_id=security_id,
        total_open_lots=len(lots_data),
        total_remaining_qty=total_remaining_qty,
        total_users_affected=len(unique_users),
        lots=lots_data
    )


