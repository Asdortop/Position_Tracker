import enum
from sqlalchemy import Column, Integer, DateTime, Numeric, Enum, CheckConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class LotStatus(str, enum.Enum):
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"
    CLOSED = "CLOSED"

class TaxLot(Base):
    __tablename__ = "tax_lots"

    # Primary key with auto-increment
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys with proper indexing
    user_id = Column(Integer, nullable=False, index=True)
    security_id = Column(Integer, nullable=False, index=True)
    
    # Version for optimistic locking
    version = Column(Integer, nullable=False, default=1)
    
    # Timestamps with timezone support
    open_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    close_date = Column(DateTime(timezone=True), nullable=True)
    
    # Quantities with precision and constraints
    open_qty = Column(Numeric(19, 4), nullable=False)
    close_qty = Column(Numeric(19, 4), nullable=False, default=0)
    remaining_qty = Column(Numeric(19, 4), nullable=False)
    
    # Prices with precision
    open_price = Column(Numeric(19, 4), nullable=False)
    close_price = Column(Numeric(19, 4), nullable=True)
    
    # Charges and P&L
    charges = Column(Numeric(19, 4), nullable=False, default=0)
    realized_pnl = Column(Numeric(19, 4), nullable=False, default=0)
    stcg = Column(Numeric(19, 4), nullable=False, default=0)
    ltcg = Column(Numeric(19, 4), nullable=False, default=0)
    
    # Status with enum
    status = Column(Enum(LotStatus, name="lot_status"), nullable=False, default=LotStatus.OPEN)
    
    # PostgreSQL-specific constraints
    __table_args__ = (
        # Check constraints for data integrity
        CheckConstraint('open_qty > 0', name='check_open_qty_positive'),
        CheckConstraint('close_qty >= 0', name='check_close_qty_non_negative'),
        CheckConstraint('remaining_qty >= 0', name='check_remaining_qty_non_negative'),
        CheckConstraint('remaining_qty <= open_qty', name='check_remaining_qty_not_exceed_open'),
        CheckConstraint('open_price > 0', name='check_open_price_positive'),
        CheckConstraint('close_price IS NULL OR close_price > 0', name='check_close_price_positive'),
        CheckConstraint('charges >= 0', name='check_charges_non_negative'),
        CheckConstraint('version > 0', name='check_version_positive'),
        
        # Composite indexes for common queries
        Index('idx_user_security_status', 'user_id', 'security_id', 'status'),
        Index('idx_user_security_date', 'user_id', 'security_id', 'open_date'),
        Index('idx_security_status_date', 'security_id', 'status', 'open_date'),
        Index('idx_user_date', 'user_id', 'open_date'),
        Index('idx_close_date', 'close_date'),
    )