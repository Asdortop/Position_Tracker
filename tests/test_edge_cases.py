import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from app.services.processing_service import processing_service
from app.models.tax_lot import TaxLot, LotStatus
from app.api.v1.schemas.trade import Trade

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_zero_quantity_trade(self, test_db):
        """Test trade with zero quantity."""
        trade = Trade(
            user_id=123,
            security_id=1,
            side="BUY",
            quantity=Decimal("0.0"),
            price=Decimal("150.0"),
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            charges=Decimal("5.0")
        )
        
        await processing_service.process_trade(test_db, trade)
        await test_db.commit()
        
        # Should create a lot with zero quantity
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.open_qty == Decimal("0.0")
        assert lot_data.remaining_qty == Decimal("0.0")

    @pytest.mark.asyncio
    async def test_very_small_quantity_trade(self, test_db):
        """Test trade with very small quantity."""
        trade = Trade(
            user_id=123,
            security_id=1,
            side="BUY",
            quantity=Decimal("0.0001"),
            price=Decimal("150.0"),
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            charges=Decimal("0.01")
        )
        
        await processing_service.process_trade(test_db, trade)
        await test_db.commit()
        
        # Should handle very small quantities
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.open_qty == Decimal("0.0001")
        assert lot_data.remaining_qty == Decimal("0.0001")

    @pytest.mark.asyncio
    async def test_very_large_quantity_trade(self, test_db):
        """Test trade with very large quantity."""
        trade = Trade(
            user_id=123,
            security_id=1,
            side="BUY",
            quantity=Decimal("999999999.9999"),
            price=Decimal("150.0"),
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            charges=Decimal("50000.0")
        )
        
        await processing_service.process_trade(test_db, trade)
        await test_db.commit()
        
        # Should handle very large quantities
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.open_qty == Decimal("999999999.9999")
        assert lot_data.remaining_qty == Decimal("999999999.9999")

    @pytest.mark.asyncio
    async def test_very_small_price_trade(self, test_db):
        """Test trade with very small price."""
        trade = Trade(
            user_id=123,
            security_id=1,
            side="BUY",
            quantity=Decimal("100.0"),
            price=Decimal("0.0001"),
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            charges=Decimal("0.01")
        )
        
        await processing_service.process_trade(test_db, trade)
        await test_db.commit()
        
        # Should handle very small prices
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.open_price == Decimal("0.0001")

    @pytest.mark.asyncio
    async def test_very_large_price_trade(self, test_db):
        """Test trade with very large price."""
        trade = Trade(
            user_id=123,
            security_id=1,
            side="BUY",
            quantity=Decimal("100.0"),
            price=Decimal("999999.9999"),
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            charges=Decimal("5000.0")
        )
        
        await processing_service.process_trade(test_db, trade)
        await test_db.commit()
        
        # Should handle very large prices
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.open_price == Decimal("999999.9999")

    @pytest.mark.asyncio
    async def test_negative_charges_handling(self, test_db):
        """Test trade with negative charges (should be treated as zero)."""
        trade = Trade(
            user_id=123,
            security_id=1,
            side="BUY",
            quantity=Decimal("100.0"),
            price=Decimal("150.0"),
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            charges=Decimal("-5.0")  # Negative charges
        )
        
        await processing_service.process_trade(test_db, trade)
        await test_db.commit()
        
        # Should handle negative charges (treated as zero in processing)
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.charges == Decimal("0.0")  # Should be zero

    @pytest.mark.asyncio
    async def test_exact_365_day_holding_period(self, test_db):
        """Test holding period exactly at 365 days (should be long-term)."""
        lot = TaxLot(
            user_id=123,
            security_id=1,
            open_date=datetime(2023, 1, 1, 10, 0, 0),
            open_qty=Decimal("100.0"),
            remaining_qty=Decimal("100.0"),
            open_price=Decimal("150.0"),
            charges=Decimal("5.0"),
            status=LotStatus.OPEN
        )
        
        test_db.add(lot)
        await test_db.commit()
        
        # Sell exactly 365 days later
        sell_trade = Trade(
            user_id=123,
            security_id=1,
            side="SELL",
            quantity=Decimal("100.0"),
            price=Decimal("170.0"),
            timestamp=datetime(2024, 1, 1, 10, 0, 0),  # Exactly 365 days
            charges=Decimal("4.0")
        )
        
        await processing_service.process_trade(test_db, sell_trade)
        await test_db.commit()
        
        # Should be treated as long-term (>= 365 days)
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE id = 1"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.ltcg > Decimal("0.0")  # Long-term tax applied
        assert lot_data.stcg == Decimal("0.0")  # No short-term tax

    @pytest.mark.asyncio
    async def test_364_day_holding_period(self, test_db):
        """Test holding period at 364 days (should be short-term)."""
        lot = TaxLot(
            user_id=123,
            security_id=1,
            open_date=datetime(2023, 1, 1, 10, 0, 0),
            open_qty=Decimal("100.0"),
            remaining_qty=Decimal("100.0"),
            open_price=Decimal("150.0"),
            charges=Decimal("5.0"),
            status=LotStatus.OPEN
        )
        
        test_db.add(lot)
        await test_db.commit()
        
        # Sell 364 days later
        sell_trade = Trade(
            user_id=123,
            security_id=1,
            side="SELL",
            quantity=Decimal("100.0"),
            price=Decimal("170.0"),
            timestamp=datetime(2023, 12, 31, 10, 0, 0),  # 364 days
            charges=Decimal("4.0")
        )
        
        await processing_service.process_trade(test_db, sell_trade)
        await test_db.commit()
        
        # Should be treated as short-term (< 365 days)
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE id = 1"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.stcg > Decimal("0.0")  # Short-term tax applied
        assert lot_data.ltcg == Decimal("0.0")  # No long-term tax

    @pytest.mark.asyncio
    async def test_sell_more_than_owned(self, test_db):
        """Test selling more quantity than owned."""
        # Create a lot with 100 shares
        lot = TaxLot(
            user_id=123,
            security_id=1,
            open_date=datetime(2024, 1, 1, 10, 0, 0),
            open_qty=Decimal("100.0"),
            remaining_qty=Decimal("100.0"),
            open_price=Decimal("150.0"),
            charges=Decimal("5.0"),
            status=LotStatus.OPEN
        )
        
        test_db.add(lot)
        await test_db.commit()
        
        # Try to sell 150 shares (more than owned)
        sell_trade = Trade(
            user_id=123,
            security_id=1,
            "side": "SELL",
            quantity=Decimal("150.0"),
            price=Decimal("170.0"),
            timestamp=datetime(2024, 2, 1, 10, 0, 0),
            charges=Decimal("4.0")
        )
        
        # This should not raise an error in current implementation
        # but should only sell what's available
        await processing_service.process_trade(test_db, sell_trade)
        await test_db.commit()
        
        # Verify only 100 shares were sold
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE id = 1"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.remaining_qty == Decimal("0.0")  # All sold
        assert lot_data.close_qty == Decimal("100.0")  # Only 100 sold, not 150

    @pytest.mark.asyncio
    async def test_multiple_small_sells(self, test_db):
        """Test multiple small sell transactions."""
        # Create a lot with 1000 shares
        lot = TaxLot(
            user_id=123,
            security_id=1,
            open_date=datetime(2024, 1, 1, 10, 0, 0),
            open_qty=Decimal("1000.0"),
            remaining_qty=Decimal("1000.0"),
            open_price=Decimal("150.0"),
            charges=Decimal("50.0"),
            status=LotStatus.OPEN
        )
        
        test_db.add(lot)
        await test_db.commit()
        
        # Sell in multiple small transactions
        for i in range(10):
            sell_trade = Trade(
                user_id=123,
                security_id=1,
                side="SELL",
                quantity=Decimal("50.0"),  # 50 shares each time
                price=Decimal("160.0"),
                timestamp=datetime(2024, 2, 1, 10, i, 0),  # Different times
                charges=Decimal("2.0")
            )
            
            await processing_service.process_trade(test_db, sell_trade)
            await test_db.commit()
        
        # Verify final state
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE id = 1"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.remaining_qty == Decimal("500.0")  # 1000 - (10 * 50)
        assert lot_data.close_qty == Decimal("500.0")
        assert lot_data.status == "PARTIAL"

    @pytest.mark.asyncio
    async def test_very_high_precision_calculations(self, test_db):
        """Test calculations with very high precision."""
        trade = Trade(
            user_id=123,
            security_id=1,
            side="BUY",
            quantity=Decimal("100.123456789"),
            price=Decimal("150.987654321"),
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            charges=Decimal("5.123456789")
        )
        
        await processing_service.process_trade(test_db, trade)
        await test_db.commit()
        
        # Verify precision is maintained
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.open_qty == Decimal("100.123456789")
        assert lot_data.open_price == Decimal("150.987654321")
        assert lot_data.charges == Decimal("5.123456789")

    @pytest.mark.asyncio
    async def test_same_timestamp_trades(self, test_db):
        """Test trades with identical timestamps."""
        trade1 = Trade(
            user_id=123,
            security_id=1,
            side="BUY",
            quantity=Decimal("100.0"),
            price=Decimal("150.0"),
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            charges=Decimal("5.0")
        )
        
        trade2 = Trade(
            user_id=123,
            security_id=1,
            side="BUY",
            quantity=Decimal("50.0"),
            price=Decimal("160.0"),
            timestamp=datetime(2024, 1, 1, 10, 0, 0),  # Same timestamp
            charges=Decimal("3.0")
        )
        
        await processing_service.process_trade(test_db, trade1)
        await processing_service.process_trade(test_db, trade2)
        await test_db.commit()
        
        # Both trades should be processed
        lots_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123 ORDER BY id"
        )
        lots = lots_result.fetchall()
        
        assert len(lots) == 2
        assert lots[0].open_qty == Decimal("100.0")
        assert lots[1].open_qty == Decimal("50.0")

    @pytest.mark.asyncio
    async def test_zero_price_trade(self, test_db):
        """Test trade with zero price (edge case)."""
        trade = Trade(
            user_id=123,
            security_id=1,
            side="BUY",
            quantity=Decimal("100.0"),
            price=Decimal("0.0"),  # Zero price
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            charges=Decimal("5.0")
        )
        
        await processing_service.process_trade(test_db, trade)
        await test_db.commit()
        
        # Should handle zero price
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.open_price == Decimal("0.0")

    @pytest.mark.asyncio
    async def test_very_large_charges(self, test_db):
        """Test trade with charges larger than the trade value."""
        trade = Trade(
            user_id=123,
            security_id=1,
            side="BUY",
            quantity=Decimal("100.0"),
            price=Decimal("150.0"),  # Trade value: 15,000
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            charges=Decimal("20000.0")  # Charges: 20,000 (larger than trade value)
        )
        
        await processing_service.process_trade(test_db, trade)
        await test_db.commit()
        
        # Should handle large charges
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.charges == Decimal("20000.0")
