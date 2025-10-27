"""
Mathematical calculation utilities for the Position Tracker API.
"""
from decimal import Decimal
from typing import Tuple


def calculate_holding_period(open_date: str, close_date: str) -> int:
    """
    Calculate the holding period in days between two dates.
    
    Args:
        open_date: Opening date string (ISO format)
        close_date: Closing date string (ISO format)
        
    Returns:
        Holding period in days
    """
    from datetime import datetime
    
    open_dt = datetime.fromisoformat(open_date.replace('Z', '+00:00'))
    close_dt = datetime.fromisoformat(close_date.replace('Z', '+00:00'))
    
    # Ensure both are timezone-naive for calculation
    if open_dt.tzinfo is not None:
        open_dt = open_dt.replace(tzinfo=None)
    if close_dt.tzinfo is not None:
        close_dt = close_dt.replace(tzinfo=None)
    
    return (close_dt - open_dt).days


def calculate_tax_rates(holding_period: int) -> Tuple[Decimal, Decimal]:
    """
    Calculate short-term and long-term capital gains tax rates.
    
    Args:
        holding_period: Number of days the security was held
        
    Returns:
        Tuple of (short_term_rate, long_term_rate) as Decimal
    """
    if holding_period < 365:
        return Decimal("0.25"), Decimal("0.00")  # 25% STCG, 0% LTCG
    else:
        return Decimal("0.00"), Decimal("0.125")  # 0% STCG, 12.5% LTCG


def calculate_realized_pnl(
    sell_price: Decimal,
    buy_price: Decimal,
    quantity: Decimal,
    charges: Decimal = Decimal("0")
) -> Decimal:
    """
    Calculate realized profit/loss.
    
    Args:
        sell_price: Price at which security was sold
        buy_price: Price at which security was bought
        quantity: Quantity of securities
        charges: Additional charges/fees
        
    Returns:
        Realized P&L
    """
    return (sell_price - buy_price) * quantity - charges


def calculate_unrealized_pnl(
    current_price: Decimal,
    avg_cost_basis: Decimal,
    quantity: Decimal
) -> Decimal:
    """
    Calculate unrealized profit/loss.
    
    Args:
        current_price: Current market price
        avg_cost_basis: Average cost basis
        quantity: Current quantity held
        
    Returns:
        Unrealized P&L
    """
    return (current_price - avg_cost_basis) * quantity


def round_decimal(value: Decimal, precision: int = 4) -> Decimal:
    """
    Round a decimal value to specified precision.
    
    Args:
        value: The decimal value to round
        precision: Number of decimal places
        
    Returns:
        Rounded decimal value
    """
    return value.quantize(Decimal('0.0001'))
