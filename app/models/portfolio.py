from sqlalchemy import Column, Integer, DateTime, Numeric, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Deprecated persistent portfolio table. Kept only for migrations/backward compat.
class Portfolio(Base):
    __tablename__ = "portfolio_summary"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    security_id = Column(Integer, nullable=False, index=True)
    quantity = Column(Numeric(19, 4), nullable=False, default=0)
    avg_cost_basis = Column(Numeric(19, 4), nullable=False, default=0)
    current_price = Column(Numeric(19, 4), nullable=False, default=0)
    unrealized_pnl = Column(Numeric(19, 4), nullable=False, default=0)
    realized_pnl_ytd = Column(Numeric(19, 4), nullable=False, default=0)
    stcg_ytd = Column(Numeric(19, 4), nullable=False, default=0)
    ltcg_ytd = Column(Numeric(19, 4), nullable=False, default=0)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())