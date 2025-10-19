import enum
from sqlalchemy import Column, Integer, DateTime, Numeric, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class LotStatus(str, enum.Enum):
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"
    CLOSED = "CLOSED"

class TaxLot(Base):
    __tablename__ = "tax_lots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    # Per final schema, use integer security id
    security_id = Column(Integer, nullable=False, index=True)
    
    # Version (store as small int)
    version = Column(Integer, nullable=False, default=1)
    
    open_date = Column(DateTime, nullable=False)
    # creation timestamp
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    close_date = Column(DateTime, nullable=True)
    
    open_qty = Column(Numeric(19, 4), nullable=False)
    close_qty = Column(Numeric(19, 4), nullable=False, default=0)
    remaining_qty = Column(Numeric(19, 4), nullable=False)
    
    open_price = Column(Numeric(19, 4), nullable=False)
    close_price = Column(Numeric(19, 4), nullable=True)
    
    # charges per lot (optional)
    charges = Column(Numeric(19, 4), nullable=False, default=0)
    
    # realized allocations
    realized_pnl = Column(Numeric(19, 4), nullable=False, default=0)
    stcg = Column(Numeric(19, 4), nullable=False, default=0)
    ltcg = Column(Numeric(19, 4), nullable=False, default=0)
    
    status = Column(Enum(LotStatus, name="lot_status"), nullable=False, default=LotStatus.OPEN)