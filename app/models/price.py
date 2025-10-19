from sqlalchemy import Column, Integer, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class SecurityPrice(Base):
    __tablename__ = "security_prices"
    security_id = Column(Integer, primary_key=True, index=True)
    price = Column(Numeric(19, 4), nullable=False)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


