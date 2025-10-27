from sqlalchemy import Column, Integer, Numeric, DateTime, CheckConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class SecurityPrice(Base):
    __tablename__ = "security_prices"
    
    # Primary key
    security_id = Column(Integer, primary_key=True, index=True)
    
    # Price with precision
    price = Column(Numeric(19, 4), nullable=False)
    
    # Timestamp with timezone support
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # PostgreSQL-specific constraints
    __table_args__ = (
        # Check constraints for data integrity
        CheckConstraint('price > 0', name='check_price_positive'),
        
        # Index for time-based queries
        Index('idx_updated_at', 'updated_at'),
    )


