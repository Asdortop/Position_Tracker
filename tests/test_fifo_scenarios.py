import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from app.services.processing_service import processing_service
from app.models.tax_lot import TaxLot, LotStatus
from app.api.v1.schemas.trade import Trade

class TestFIFOScenarios:
    """Test complex FIFO scenarios and edge cases."""

    @pytest.mark.asyncio
    async def test_complex_fifo_scenario_1(self, test_db):
        """Test complex FIFO scenario with multiple lots and partial sales."""
        # Create multiple buy lots
        lots_data = [
            {"qty": 100, "price": 150.0, "date": "2024-01-01", "charges": 5.0},
            {"qty": 200, "price": 160.0, "date": "2024-01-15", "charges": 8.0},
            {"qty": 150, "price": 155.0, "date": "2024-02-01", "charges": 6.0},
            {"qty": 300, "price": 170.0, "date": "2024-02-15", "charges": 12.0},
        ]
        
        for lot_data in lots_data:
            lot = TaxLot(
                user_id=123,
                security_id=1,
                open_date=datetime.fromisoformat(lot_data["date"]),
                open_qty=Decimal(str(lot_data["qty"])),
                remaining_qty=Decimal(str(lot_data["qty"])),
                open_price=Decimal(str(lot_data["price"])),
                charges=Decimal(str(lot_data["charges"])),
                status=LotStatus.OPEN
            )
            test_db.add(lot)
        
        await test_db.commit()
        
        # Sell 400 shares (should consume: 100 + 200 + 100 from third lot)
        sell_trade = Trade(
            user_id=123,
            security_id=1,
            side="SELL",
            quantity=Decimal("400.0"),
            price=Decimal("180.0"),
            timestamp=datetime(2024, 3, 1, 10, 0, 0),
            charges=Decimal("15.0")
        )
        
        await processing_service.process_trade(test_db, sell_trade)
        await test_db.commit()
        
        # Verify FIFO order
        lots_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123 ORDER BY open_date"
        )
        lots = lots_result.fetchall()
        
        # First lot: completely closed
        assert lots[0].remaining_qty == Decimal("0.0")
        assert lots[0].close_qty == Decimal("100.0")
        assert lots[0].status == "CLOSED"
        
        # Second lot: completely closed
        assert lots[1].remaining_qty == Decimal("0.0")
        assert lots[1].close_qty == Decimal("200.0")
        assert lots[1].status == "CLOSED"
        
        # Third lot: partially closed
        assert lots[2].remaining_qty == Decimal("50.0")  # 150 - 100
        assert lots[2].close_qty == Decimal("100.0")
        assert lots[2].status == "PARTIAL"
        
        # Fourth lot: unchanged
        assert lots[3].remaining_qty == Decimal("300.0")
        assert lots[3].close_qty == Decimal("0.0")
        assert lots[3].status == "OPEN"

    @pytest.mark.asyncio
    async def test_fifo_with_mixed_holding_periods(self, test_db):
        """Test FIFO with mixed short-term and long-term holdings."""
        # Create lots with different holding periods
        lot1 = TaxLot(
            user_id=123,
            security_id=1,
            open_date=datetime(2023, 1, 1, 10, 0, 0),  # Long-term
            open_qty=Decimal("100.0"),
            remaining_qty=Decimal("100.0"),
            open_price=Decimal("150.0"),
            charges=Decimal("5.0"),
            status=LotStatus.OPEN
        )
        
        lot2 = TaxLot(
            user_id=123,
            security_id=1,
            open_date=datetime(2024, 1, 1, 10, 0, 0),  # Short-term
            open_qty=Decimal("200.0"),
            remaining_qty=Decimal("200.0"),
            open_price=Decimal("160.0"),
            charges=Decimal("8.0"),
            status=LotStatus.OPEN
        )
        
        test_db.add(lot1)
        test_db.add(lot2)
        await test_db.commit()
        
        # Sell 150 shares (100 from lot1 + 50 from lot2)
        sell_trade = Trade(
            user_id=123,
            security_id=1,
            side="SELL",
            quantity=Decimal("150.0"),
            price=Decimal("180.0"),
            timestamp=datetime(2024, 2, 1, 10, 0, 0),
            charges=Decimal("10.0")
        )
        
        await processing_service.process_trade(test_db, sell_trade)
        await test_db.commit()
        
        # Verify tax calculations
        lots_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123 ORDER BY open_date"
        )
        lots = lots_result.fetchall()
        
        # First lot: long-term, completely closed
        assert lots[0].status == "CLOSED"
        assert lots[0].ltcg > Decimal("0.0")  # Long-term tax
        assert lots[0].stcg == Decimal("0.0")  # No short-term tax
        
        # Second lot: short-term, partially closed
        assert lots[1].status == "PARTIAL"
        assert lots[1].stcg > Decimal("0.0")  # Short-term tax
        assert lots[1].ltcg == Decimal("0.0")  # No long-term tax

    @pytest.mark.asyncio
    async def test_fifo_with_identical_prices(self, test_db):
        """Test FIFO with lots having identical prices."""
        # Create lots with same price but different dates
        lot1 = TaxLot(
            user_id=123,
            security_id=1,
            open_date=datetime(2024, 1, 1, 10, 0, 0),
            open_qty=Decimal("100.0"),
            remaining_qty=Decimal("100.0"),
            open_price=Decimal("150.0"),
            charges=Decimal("5.0"),
            status=LotStatus.OPEN
        )
        
        lot2 = TaxLot(
            user_id=123,
            security_id=1,
            open_date=datetime(2024, 1, 15, 10, 0, 0),
            open_qty=Decimal("100.0"),
            remaining_qty=Decimal("100.0"),
            open_price=Decimal("150.0"),  # Same price
            charges=Decimal("5.0"),
            status=LotStatus.OPEN
        )
        
        test_db.add(lot1)
        test_db.add(lot2)
        await test_db.commit()
        
        # Sell 150 shares
        sell_trade = Trade(
            user_id=123,
            security_id=1,
            side="SELL",
            quantity=Decimal("150.0"),
            price=Decimal("160.0"),
            timestamp=datetime(2024, 2, 1, 10, 0, 0),
            charges=Decimal("8.0")
        )
        
        await processing_service.process_trade(test_db, sell_trade)
        await test_db.commit()
        
        # Verify FIFO order (by date, not price)
        lots_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123 ORDER BY open_date"
        )
        lots = lots_result.fetchall()
        
        # First lot: completely closed
        assert lots[0].remaining_qty == Decimal("0.0")
        assert lots[0].status == "CLOSED"
        
        # Second lot: partially closed
        assert lots[1].remaining_qty == Decimal("50.0")
        assert lots[1].status == "PARTIAL"

    @pytest.mark.asyncio
    async def test_fifo_with_zero_remaining_after_sell(self, test_db):
        """Test FIFO when sell quantity exactly matches remaining quantity."""
        # Create a lot
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
        
        # Sell exactly 100 shares
        sell_trade = Trade(
            user_id=123,
            security_id=1,
            side="SELL",
            quantity=Decimal("100.0"),
            price=Decimal("160.0"),
            timestamp=datetime(2024, 2, 1, 10, 0, 0),
            charges=Decimal("8.0")
        )
        
        await processing_service.process_trade(test_db, sell_trade)
        await test_db.commit()
        
        # Verify lot is completely closed
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.remaining_qty == Decimal("0.0")
        assert lot_data.close_qty == Decimal("100.0")
        assert lot_data.status == "CLOSED"

    @pytest.mark.asyncio
    async def test_fifo_with_multiple_sells_same_lot(self, test_db):
        """Test multiple sells from the same lot."""
        # Create a large lot
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
        
        # First sell: 300 shares
        sell1 = Trade(
            user_id=123,
            security_id=1,
            side="SELL",
            quantity=Decimal("300.0"),
            price=Decimal("160.0"),
            timestamp=datetime(2024, 2, 1, 10, 0, 0),
            charges=Decimal("15.0")
        )
        
        await processing_service.process_trade(test_db, sell1)
        await test_db.commit()
        
        # Verify first sell
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.remaining_qty == Decimal("700.0")
        assert lot_data.close_qty == Decimal("300.0")
        assert lot_data.status == "PARTIAL"
        
        # Second sell: 400 shares
        sell2 = Trade(
            user_id=123,
            security_id=1,
            side="SELL",
            quantity=Decimal("400.0"),
            price=Decimal("170.0"),
            timestamp=datetime(2024, 2, 15, 10, 0, 0),
            charges=Decimal("20.0")
        )
        
        await processing_service.process_trade(test_db, sell2)
        await test_db.commit()
        
        # Verify second sell
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.remaining_qty == Decimal("300.0")
        assert lot_data.close_qty == Decimal("700.0")
        assert lot_data.status == "PARTIAL"
        
        # Third sell: remaining 300 shares
        sell3 = Trade(
            user_id=123,
            security_id=1,
            side="SELL",
            quantity=Decimal("300.0"),
            price=Decimal("180.0"),
            timestamp=datetime(2024, 3, 1, 10, 0, 0),
            charges=Decimal("15.0")
        )
        
        await processing_service.process_trade(test_db, sell3)
        await test_db.commit()
        
        # Verify final state
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.remaining_qty == Decimal("0.0")
        assert lot_data.close_qty == Decimal("1000.0")
        assert lot_data.status == "CLOSED"

    @pytest.mark.asyncio
    async def test_fifo_with_very_small_quantities(self, test_db):
        """Test FIFO with very small quantities."""
        # Create lots with small quantities
        lot1 = TaxLot(
            user_id=123,
            security_id=1,
            open_date=datetime(2024, 1, 1, 10, 0, 0),
            open_qty=Decimal("0.0001"),
            remaining_qty=Decimal("0.0001"),
            open_price=Decimal("150.0"),
            charges=Decimal("0.01"),
            status=LotStatus.OPEN
        )
        
        lot2 = TaxLot(
            user_id=123,
            security_id=1,
            open_date=datetime(2024, 1, 2, 10, 0, 0),
            open_qty=Decimal("0.0002"),
            remaining_qty=Decimal("0.0002"),
            open_price=Decimal("160.0"),
            charges=Decimal("0.02"),
            status=LotStatus.OPEN
        )
        
        test_db.add(lot1)
        test_db.add(lot2)
        await test_db.commit()
        
        # Sell 0.00015 shares (should consume all of lot1 and 0.00005 from lot2)
        sell_trade = Trade(
            user_id=123,
            security_id=1,
            side="SELL",
            quantity=Decimal("0.00015"),
            price=Decimal("170.0"),
            timestamp=datetime(2024, 2, 1, 10, 0, 0),
            charges=Decimal("0.01")
        )
        
        await processing_service.process_trade(test_db, sell_trade)
        await test_db.commit()
        
        # Verify FIFO order
        lots_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123 ORDER BY open_date"
        )
        lots = lots_result.fetchall()
        
        # First lot: completely closed
        assert lots[0].remaining_qty == Decimal("0.0")
        assert lots[0].status == "CLOSED"
        
        # Second lot: partially closed
        assert lots[1].remaining_qty == Decimal("0.00015")  # 0.0002 - 0.00005
        assert lots[1].status == "PARTIAL"

    @pytest.mark.asyncio
    async def test_fifo_with_high_precision_calculations(self, test_db):
        """Test FIFO with high precision decimal calculations."""
        # Create lots with high precision
        lot1 = TaxLot(
            user_id=123,
            security_id=1,
            open_date=datetime(2024, 1, 1, 10, 0, 0),
            open_qty=Decimal("100.123456789"),
            remaining_qty=Decimal("100.123456789"),
            open_price=Decimal("150.987654321"),
            charges=Decimal("5.123456789"),
            status=LotStatus.OPEN
        )
        
        lot2 = TaxLot(
            user_id=123,
            security_id=1,
            open_date=datetime(2024, 1, 2, 10, 0, 0),
            open_qty=Decimal("200.987654321"),
            remaining_qty=Decimal("200.987654321"),
            open_price=Decimal("160.123456789"),
            charges=Decimal("8.987654321"),
            status=LotStatus.OPEN
        )
        
        test_db.add(lot1)
        test_db.add(lot2)
        await test_db.commit()
        
        # Sell 150.5 shares
        sell_trade = Trade(
            user_id=123,
            security_id=1,
            side="SELL",
            quantity=Decimal("150.5"),
            price=Decimal("170.5"),
            timestamp=datetime(2024, 2, 1, 10, 0, 0),
            charges=Decimal("10.5")
        )
        
        await processing_service.process_trade(test_db, sell_trade)
        await test_db.commit()
        
        # Verify FIFO order with precision
        lots_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123 ORDER BY open_date"
        )
        lots = lots_result.fetchall()
        
        # First lot: completely closed
        assert lots[0].remaining_qty == Decimal("0.0")
        assert lots[0].status == "CLOSED"
        
        # Second lot: partially closed
        expected_remaining = Decimal("200.987654321") - (Decimal("150.5") - Decimal("100.123456789"))
        assert abs(lots[1].remaining_qty - expected_remaining) < Decimal("0.000000001")
        assert lots[1].status == "PARTIAL"
