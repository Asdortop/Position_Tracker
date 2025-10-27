"""
Tax calculation service for the Position Tracker API.
"""
from decimal import Decimal
from typing import Tuple

from app.utils.calculation_utils import calculate_holding_period, calculate_tax_rates


class TaxService:
    """Service for handling tax calculations."""
    
    @staticmethod
    def calculate_tax_lot_taxes(
        open_date: str,
        close_date: str,
        sell_price: Decimal,
        buy_price: Decimal,
        quantity: Decimal,
        charges: Decimal = Decimal("0")
    ) -> Tuple[Decimal, Decimal, Decimal, Decimal]:
        """
        Calculate taxes for a tax lot.
        
        Args:
            open_date: Opening date of the lot
            close_date: Closing date of the lot
            sell_price: Price at which security was sold
            buy_price: Price at which security was bought
            quantity: Quantity of securities
            charges: Additional charges/fees
            
        Returns:
            Tuple of (realized_pnl, stcg, ltcg, total_tax)
        """
        # Calculate holding period
        holding_period = calculate_holding_period(open_date, close_date)
        
        # Calculate realized P&L
        realized_pnl = (sell_price - buy_price) * quantity - charges
        
        # Get tax rates
        stcg_rate, ltcg_rate = calculate_tax_rates(holding_period)
        
        # Calculate taxes
        if holding_period < 365:
            stcg = realized_pnl * stcg_rate
            ltcg = Decimal("0")
        else:
            stcg = Decimal("0")
            ltcg = realized_pnl * ltcg_rate
        
        total_tax = stcg + ltcg
        
        return realized_pnl, stcg, ltcg, total_tax
    
    @staticmethod
    def calculate_annual_tax_summary(tax_lots: list) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Calculate annual tax summary from tax lots.
        
        Args:
            tax_lots: List of tax lot objects
            
        Returns:
            Tuple of (total_stcg, total_ltcg, total_realized_pnl)
        """
        total_stcg = Decimal("0")
        total_ltcg = Decimal("0")
        total_realized_pnl = Decimal("0")
        
        for lot in tax_lots:
            total_stcg += lot.stcg or Decimal("0")
            total_ltcg += lot.ltcg or Decimal("0")
            total_realized_pnl += lot.realized_pnl or Decimal("0")
        
        return total_stcg, total_ltcg, total_realized_pnl
