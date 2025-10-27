from sqlalchemy import Column, Integer, DateTime, Numeric, func, CheckConstraint, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Deprecated persistent portfolio table. Kept only for migrations/backward compat.
class Portfolio(Base):
    __tablename__ = "portfolio_summary"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys with proper indexing
    user_id = Column(Integer, nullable=False, index=True)
    security_id = Column(Integer, nullable=False, index=True)
    
    # Portfolio metrics with precision
    quantity = Column(Numeric(19, 4), nullable=False, default=0)
    avg_cost_basis = Column(Numeric(19, 4), nullable=False, default=0)
    current_price = Column(Numeric(19, 4), nullable=False, default=0)
    unrealized_pnl = Column(Numeric(19, 4), nullable=False, default=0)
    realized_pnl_ytd = Column(Numeric(19, 4), nullable=False, default=0)
    stcg_ytd = Column(Numeric(19, 4), nullable=False, default=0)
    ltcg_ytd = Column(Numeric(19, 4), nullable=False, default=0)
    
    # Timestamp with timezone support
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # PostgreSQL-specific constraints
    __table_args__ = (
        # Check constraints for data integrity
        CheckConstraint('quantity >= 0', name='check_quantity_non_negative'),
        CheckConstraint('avg_cost_basis >= 0', name='check_avg_cost_basis_non_negative'),
        CheckConstraint('current_price >= 0', name='check_current_price_non_negative'),
        CheckConstraint('stcg_ytd >= 0', name='check_stcg_ytd_non_negative'),
        CheckConstraint('ltcg_ytd >= 0', name='check_ltcg_ytd_non_negative'),
        
        # Composite indexes for common queries
        Index('idx_user_security', 'user_id', 'security_id'),
        Index('idx_user_last_updated', 'user_id', 'last_updated'),
        Index('idx_last_updated', 'last_updated'),
        
        # Unique constraint to prevent duplicate portfolio entries
        Index('idx_unique_user_security', 'user_id', 'security_id', unique=True),
    )