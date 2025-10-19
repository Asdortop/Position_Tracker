from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1 import dependencies
from app.api.v1.schemas.portfolio import PortfolioSnapshot
from app.services.portfolio_service import portfolio_service

router = APIRouter()

@router.get(
    "/{user_id}/snapshot",
    response_model=PortfolioSnapshot,
    summary="Get Portfolio Snapshot",
    description="Retrieve a full snapshot of a user's portfolio, including positions and P&L summaries.",
)
async def read_portfolio_snapshot(
    user_id: int,
    db: AsyncSession = Depends(dependencies.get_db),
    # current_user: dict = Depends(dependencies.get_current_user) # Uncomment for auth
):
    """
    Retrieves the complete portfolio snapshot for a user.
    - **user_id**: The ID of the user whose portfolio is being requested.
    """
    # Authorization check would go here:
    # if current_user['id'] != user_id:
    #     raise HTTPException(status_code=403, detail="Not authorized")
        
    snapshot = await portfolio_service.get_portfolio_snapshot(db=db, user_id=user_id)
    return snapshot