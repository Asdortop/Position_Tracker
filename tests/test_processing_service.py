import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from app.services.processing_service import processing_service
from app.models.tax_lot import TaxLot, LotStatus
from app.api.v1.schemas.trade import Trade

class TestProcessingService:
    """Test cases for the core processing service business logic."""

    @pytest.mark.asyncio
    async def test_buy_trade_processing(self, test_db):
        """Test basic buy trade processing."""
        trade = Trade(
            user_id=123,
            security_id=1,
            side="BUY",
            quantity=Decimal("100.0"),
            price=Decimal("150.0"),
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            charges=Decimal("5.0")
        )
        
        await processing_service.process_trade(test_db, trade)
        await test_db.commit()
        
        # Verify tax lot was created
        lots = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123 AND security_id = 1"
        )
        lot = lots.fetchone()
        
        assert lot is not None
        assert lot.user_id == 123
        assert lot.security_id == 1
        assert lot.open_qty == Decimal("100.0")
        assert lot.remaining_qty == Decimal("100.0")
        assert lot.open_price == Decimal("150.0")
        assert lot.charges == Decimal("5.0")
        assert lot.status == "OPEN"

    @pytest.mark.asyncio
    async def test_sell_trade_fifo_processing(self, test_db):
        """Test sell trade processing with FIFO logic."""
        # Create multiple buy lots
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
            open_qty=Decimal("50.0"),
            remaining_qty=Decimal("50.0"),
            open_price=Decimal("160.0"),
            charges=Decimal("3.0"),
            status=LotStatus.OPEN
        )
        
        test_db.add(lot1)
        test_db.add(lot2)
        await test_db.commit()
        
        # Sell 75 shares (should consume 75 from first lot)
        sell_trade = Trade(
            user_id=123,
            security_id=1,
            side="SELL",
            quantity=Decimal("75.0"),
            price=Decimal("170.0"),
            timestamp=datetime(2024, 2, 1, 10, 0, 0),
            charges=Decimal("4.0")
        )
        
        await processing_service.process_trade(test_db, sell_trade)
        await test_db.commit()
        
        # Verify first lot is partially closed
        lot1_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE id = 1"
        )
        lot1_data = lot1_result.fetchone()
        
        assert lot1_data.remaining_qty == Decimal("25.0")  # 100 - 75
        assert lot1_data.close_qty == Decimal("75.0")
        assert lot1_data.status == "PARTIAL"
        assert lot1_data.close_date == datetime(2024, 2, 1, 10, 0, 0)
        assert lot1_data.close_price == Decimal("170.0")
        
        # Verify second lot is unchanged
        lot2_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE id = 2"
        )
        lot2_data = lot2_result.fetchone()
        
        assert lot2_data.remaining_qty == Decimal("50.0")
        assert lot2_data.status == "OPEN"

    @pytest.mark.asyncio
    async def test_sell_trade_multiple_lots_fifo(self, test_db):
        """Test sell trade that spans multiple lots in FIFO order."""
        # Create multiple buy lots
        lot1 = TaxLot(
            user_id=123,
            security_id=1,
            open_date=datetime(2024, 1, 1, 10, 0, 0),
            open_qty=Decimal("50.0"),
            remaining_qty=Decimal("50.0"),
            open_price=Decimal("150.0"),
            charges=Decimal("2.5"),
            status=LotStatus.OPEN
        )
        
        lot2 = TaxLot(
            user_id=123,
            security_id=1,
            open_date=datetime(2024, 1, 15, 10, 0, 0),
            open_qty=Decimal("30.0"),
            remaining_qty=Decimal("30.0"),
            open_price=Decimal("160.0"),
            charges=Decimal("1.5"),
            status=LotStatus.OPEN
        )
        
        test_db.add(lot1)
        test_db.add(lot2)
        await test_db.commit()
        
        # Sell 60 shares (should consume all of lot1 and 10 from lot2)
        sell_trade = Trade(
            user_id=123,
            security_id=1,
            side="SELL",
            quantity=Decimal("60.0"),
            price=Decimal("170.0"),
            timestamp=datetime(2024, 2, 1, 10, 0, 0),
            charges=Decimal("3.0")
        )
        
        await processing_service.process_trade(test_db, sell_trade)
        await test_db.commit()
        
        # Verify first lot is completely closed
        lot1_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE id = 1"
        )
        lot1_data = lot1_result.fetchone()
        
        assert lot1_data.remaining_qty == Decimal("0.0")
        assert lot1_data.close_qty == Decimal("50.0")
        assert lot1_data.status == "CLOSED"
        
        # Verify second lot is partially closed
        lot2_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE id = 2"
        )
        lot2_data = lot2_result.fetchone()
        
        assert lot2_data.remaining_qty == Decimal("20.0")  # 30 - 10
        assert lot2_data.close_qty == Decimal("10.0")
        assert lot2_data.status == "PARTIAL"

    @pytest.mark.asyncio
    async def test_short_term_capital_gains_calculation(self, test_db):
        """Test short-term capital gains tax calculation."""
        # Create a lot with short-term holding period
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
        
        # Sell after 30 days (short-term)
        sell_trade = Trade(
            user_id=123,
            security_id=1,
            side="SELL",
            quantity=Decimal("100.0"),
            price=Decimal("170.0"),
            timestamp=datetime(2024, 1, 31, 10, 0, 0),  # 30 days later
            charges=Decimal("4.0")
        )
        
        await processing_service.process_trade(test_db, sell_trade)
        await test_db.commit()
        
        # Verify tax calculation
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE id = 1"
        )
        lot_data = lot_result.fetchone()
        
        # Gross gain: (170 - 150) * 100 = 2000
        # Charges: (5/100 + 4/100) * 100 = 9
        # Taxable gain: 2000 - 9 = 1991
        # STCG tax: 1991 * 0.25 = 497.75
        expected_taxable_gain = Decimal("1991.0")
        expected_stcg = Decimal("497.75")
        
        assert lot_data.realized_pnl == expected_taxable_gain
        assert lot_data.stcg == expected_stcg
        assert lot_data.ltcg == Decimal("0.0")

    @pytest.mark.asyncio
    async def test_long_term_capital_gains_calculation(self, test_db):
        """Test long-term capital gains tax calculation."""
        # Create a lot with long-term holding period
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
        
        # Sell after 400 days (long-term)
        sell_trade = Trade(
            user_id=123,
            security_id=1,
            side="SELL",
            quantity=Decimal("100.0"),
            price=Decimal("170.0"),
            timestamp=datetime(2024, 2, 5, 10, 0, 0),  # 400 days later
            charges=Decimal("4.0")
        )
        
        await processing_service.process_trade(test_db, sell_trade)
        await test_db.commit()
        
        # Verify tax calculation
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE id = 1"
        )
        lot_data = lot_result.fetchone()
        
        # Gross gain: (170 - 150) * 100 = 2000
        # Charges: (5/100 + 4/100) * 100 = 9
        # Taxable gain: 2000 - 9 = 1991
        # LTCG tax: 1991 * 0.125 = 248.875
        expected_taxable_gain = Decimal("1991.0")
        expected_ltcg = Decimal("248.875")
        
        assert lot_data.realized_pnl == expected_taxable_gain
        assert lot_data.stcg == Decimal("0.0")
        assert lot_data.ltcg == expected_ltcg

    @pytest.mark.asyncio
    async def test_loss_calculation(self, test_db):
        """Test loss calculation (no tax on losses)."""
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
        
        # Sell at a loss
        sell_trade = Trade(
            user_id=123,
            security_id=1,
            side="SELL",
            quantity=Decimal("100.0"),
            price=Decimal("130.0"),  # Loss
            timestamp=datetime(2024, 1, 31, 10, 0, 0),
            charges=Decimal("4.0")
        )
        
        await processing_service.process_trade(test_db, sell_trade)
        await test_db.commit()
        
        # Verify loss calculation
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE id = 1"
        )
        lot_data = lot_result.fetchone()
        
        # Gross loss: (130 - 150) * 100 = -2000
        # Charges: (5/100 + 4/100) * 100 = 9
        # Taxable loss: -2000 - 9 = -2009
        # No tax on losses
        expected_taxable_loss = Decimal("-2009.0")
        
        assert lot_data.realized_pnl == expected_taxable_loss
        assert lot_data.stcg == Decimal("0.0")
        assert lot_data.ltcg == Decimal("0.0")

    @pytest.mark.asyncio
    async def test_zero_charges(self, test_db):
        """Test trade processing with zero charges."""
        trade = Trade(
            user_id=123,
            security_id=1,
            side="BUY",
            quantity=Decimal("100.0"),
            price=Decimal("150.0"),
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            charges=Decimal("0.0")
        )
        
        await processing_service.process_trade(test_db, trade)
        await test_db.commit()
        
        # Verify lot was created with zero charges
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.charges == Decimal("0.0")

    @pytest.mark.asyncio
    async def test_none_charges(self, test_db):
        """Test trade processing with None charges."""
        trade = Trade(
            user_id=123,
            security_id=1,
            side="BUY",
            quantity=Decimal("100.0"),
            price=Decimal("150.0"),
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            charges=None
        )
        
        await processing_service.process_trade(test_db, trade)
        await test_db.commit()
        
        # Verify lot was created with zero charges
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.charges == Decimal("0.0")

    @pytest.mark.asyncio
    async def test_decimal_precision(self, test_db):
        """Test decimal precision handling."""
        trade = Trade(
            user_id=123,
            security_id=1,
            side="BUY",
            quantity=Decimal("100.1234"),
            price=Decimal("150.5678"),
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            charges=Decimal("5.9999")
        )
        
        await processing_service.process_trade(test_db, trade)
        await test_db.commit()
        
        # Verify decimal precision is maintained
        lot_result = await test_db.execute(
            "SELECT * FROM tax_lots WHERE user_id = 123"
        )
        lot_data = lot_result.fetchone()
        
        assert lot_data.open_qty == Decimal("100.1234")
        assert lot_data.open_price == Decimal("150.5678")
        assert lot_data.charges == Decimal("5.9999")
