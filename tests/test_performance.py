import pytest
import asyncio
import time
from decimal import Decimal
from datetime import datetime, timedelta
from app.services.processing_service import processing_service
from app.models.tax_lot import TaxLot, LotStatus
from app.api.v1.schemas.trade import Trade

class TestPerformance:
    """Performance tests for the position tracker system."""

    @pytest.mark.asyncio
    async def test_large_dataset_performance(self, test_db):
        """Test performance with large dataset."""
        # Create 1000 tax lots
        lots = []
        for i in range(1000):
            lot = TaxLot(
                user_id=123,
                security_id=1,
                open_date=datetime(2024, 1, 1, 10, 0, 0) + timedelta(days=i),
                open_qty=Decimal("100.0"),
                remaining_qty=Decimal("100.0"),
                open_price=Decimal("150.0") + Decimal(str(i)),
                charges=Decimal("5.0"),
                status=LotStatus.OPEN
            )
            lots.append(lot)
        
        start_time = time.time()
        for lot in lots:
            test_db.add(lot)
        await test_db.commit()
        insert_time = time.time() - start_time
        
        print(f"Inserted 1000 lots in {insert_time:.2f} seconds")
        assert insert_time < 10.0  # Should complete within 10 seconds

    @pytest.mark.asyncio
    async def test_bulk_trade_processing_performance(self, test_db):
        """Test performance of bulk trade processing."""
        # Create initial lots
        for i in range(100):
            lot = TaxLot(
                user_id=123,
                security_id=1,
                open_date=datetime(2024, 1, 1, 10, 0, 0) + timedelta(days=i),
                open_qty=Decimal("100.0"),
                remaining_qty=Decimal("100.0"),
                open_price=Decimal("150.0"),
                charges=Decimal("5.0"),
                status=LotStatus.OPEN
            )
            test_db.add(lot)
        
        await test_db.commit()
        
        # Process 50 sell trades
        start_time = time.time()
        for i in range(50):
            trade = Trade(
                user_id=123,
                security_id=1,
                side="SELL",
                quantity=Decimal("10.0"),
                price=Decimal("160.0"),
                timestamp=datetime(2024, 2, 1, 10, 0, 0) + timedelta(minutes=i),
                charges=Decimal("1.0")
            )
            await processing_service.process_trade(test_db, trade)
            await test_db.commit()
        
        processing_time = time.time() - start_time
        print(f"Processed 50 trades in {processing_time:.2f} seconds")
        assert processing_time < 5.0  # Should complete within 5 seconds

    @pytest.mark.asyncio
    async def test_concurrent_trade_processing(self, test_db):
        """Test concurrent trade processing performance."""
        # Create initial lots
        for i in range(50):
            lot = TaxLot(
                user_id=123,
                security_id=1,
                open_date=datetime(2024, 1, 1, 10, 0, 0) + timedelta(days=i),
                open_qty=Decimal("100.0"),
                remaining_qty=Decimal("100.0"),
                open_price=Decimal("150.0"),
                charges=Decimal("5.0"),
                status=LotStatus.OPEN
            )
            test_db.add(lot)
        
        await test_db.commit()
        
        # Create concurrent trades
        async def process_trade(trade_id):
            trade = Trade(
                user_id=123,
                security_id=1,
                side="SELL",
                quantity=Decimal("5.0"),
                price=Decimal("160.0"),
                timestamp=datetime(2024, 2, 1, 10, 0, 0) + timedelta(minutes=trade_id),
                charges=Decimal("1.0")
            )
            await processing_service.process_trade(test_db, trade)
            await test_db.commit()
        
        # Process 20 trades concurrently
        start_time = time.time()
        tasks = [process_trade(i) for i in range(20)]
        await asyncio.gather(*tasks)
        concurrent_time = time.time() - start_time
        
        print(f"Processed 20 concurrent trades in {concurrent_time:.2f} seconds")
        assert concurrent_time < 10.0  # Should complete within 10 seconds

    @pytest.mark.asyncio
    async def test_portfolio_snapshot_performance(self, test_db):
        """Test portfolio snapshot performance with large dataset."""
        from app.services.portfolio_service import portfolio_service
        
        # Create lots for multiple securities
        for security_id in range(1, 11):  # 10 securities
            for i in range(100):  # 100 lots per security
                lot = TaxLot(
                    user_id=123,
                    security_id=security_id,
                    open_date=datetime(2024, 1, 1, 10, 0, 0) + timedelta(days=i),
                    open_qty=Decimal("100.0"),
                    remaining_qty=Decimal("100.0"),
                    open_price=Decimal("150.0") + Decimal(str(security_id)),
                    charges=Decimal("5.0"),
                    status=LotStatus.OPEN
                )
                test_db.add(lot)
        
        await test_db.commit()
        
        # Test portfolio snapshot performance
        start_time = time.time()
        snapshot = await portfolio_service.get_portfolio_snapshot(test_db, 123)
        snapshot_time = time.time() - start_time
        
        print(f"Generated portfolio snapshot in {snapshot_time:.2f} seconds")
        assert snapshot_time < 2.0  # Should complete within 2 seconds
        assert len(snapshot.positions) == 10  # 10 securities

    @pytest.mark.asyncio
    async def test_memory_usage_large_dataset(self, test_db):
        """Test memory usage with large dataset."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create 5000 lots
        lots = []
        for i in range(5000):
            lot = TaxLot(
                user_id=123,
                security_id=1,
                open_date=datetime(2024, 1, 1, 10, 0, 0) + timedelta(days=i),
                open_qty=Decimal("100.0"),
                remaining_qty=Decimal("100.0"),
                open_price=Decimal("150.0"),
                charges=Decimal("5.0"),
                status=LotStatus.OPEN
            )
            lots.append(lot)
        
        for lot in lots:
            test_db.add(lot)
        await test_db.commit()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage increased by {memory_increase:.2f} MB for 5000 lots")
        assert memory_increase < 100.0  # Should not increase by more than 100MB

    @pytest.mark.asyncio
    async def test_database_query_performance(self, test_db):
        """Test database query performance."""
        # Create test data
        for i in range(1000):
            lot = TaxLot(
                user_id=123,
                security_id=1,
                open_date=datetime(2024, 1, 1, 10, 0, 0) + timedelta(days=i),
                open_qty=Decimal("100.0"),
                remaining_qty=Decimal("100.0"),
                open_price=Decimal("150.0"),
                charges=Decimal("5.0"),
                status=LotStatus.OPEN
            )
            test_db.add(lot)
        
        await test_db.commit()
        
        # Test query performance
        start_time = time.time()
        
        # Query all lots for user
        from sqlalchemy.future import select
        result = await test_db.execute(
            select(TaxLot).where(TaxLot.user_id == 123)
        )
        lots = result.scalars().all()
        
        query_time = time.time() - start_time
        
        print(f"Queried 1000 lots in {query_time:.2f} seconds")
        assert query_time < 1.0  # Should complete within 1 second
        assert len(lots) == 1000

    @pytest.mark.asyncio
    async def test_tax_calculation_performance(self, test_db):
        """Test tax calculation performance with many lots."""
        # Create lots with different holding periods
        lots = []
        for i in range(500):
            # Mix of short-term and long-term
            if i % 2 == 0:
                open_date = datetime(2024, 1, 1, 10, 0, 0)  # Short-term
            else:
                open_date = datetime(2023, 1, 1, 10, 0, 0)  # Long-term
            
            lot = TaxLot(
                user_id=123,
                security_id=1,
                open_date=open_date,
                open_qty=Decimal("100.0"),
                remaining_qty=Decimal("100.0"),
                open_price=Decimal("150.0"),
                charges=Decimal("5.0"),
                status=LotStatus.OPEN
            )
            lots.append(lot)
        
        for lot in lots:
            test_db.add(lot)
        await test_db.commit()
        
        # Test tax calculation performance
        start_time = time.time()
        
        # Sell all lots
        for i in range(500):
            trade = Trade(
                user_id=123,
                security_id=1,
                side="SELL",
                quantity=Decimal("100.0"),
                price=Decimal("160.0"),
                timestamp=datetime(2024, 2, 1, 10, 0, 0) + timedelta(minutes=i),
                charges=Decimal("5.0")
            )
            await processing_service.process_trade(test_db, trade)
            await test_db.commit()
        
        tax_calculation_time = time.time() - start_time
        
        print(f"Calculated taxes for 500 lots in {tax_calculation_time:.2f} seconds")
        assert tax_calculation_time < 10.0  # Should complete within 10 seconds

    @pytest.mark.asyncio
    async def test_fifo_performance_large_dataset(self, test_db):
        """Test FIFO performance with large dataset."""
        # Create 1000 lots
        for i in range(1000):
            lot = TaxLot(
                user_id=123,
                security_id=1,
                open_date=datetime(2024, 1, 1, 10, 0, 0) + timedelta(minutes=i),
                open_qty=Decimal("100.0"),
                remaining_qty=Decimal("100.0"),
                open_price=Decimal("150.0"),
                charges=Decimal("5.0"),
                status=LotStatus.OPEN
            )
            test_db.add(lot)
        
        await test_db.commit()
        
        # Test FIFO performance
        start_time = time.time()
        
        # Sell 50000 shares (should consume 500 lots)
        trade = Trade(
            user_id=123,
            security_id=1,
            side="SELL",
            quantity=Decimal("50000.0"),
            price=Decimal("160.0"),
            timestamp=datetime(2024, 2, 1, 10, 0, 0),
            charges=Decimal("100.0")
        )
        
        await processing_service.process_trade(test_db, trade)
        await test_db.commit()
        
        fifo_time = time.time() - start_time
        
        print(f"Processed FIFO for 50000 shares in {fifo_time:.2f} seconds")
        assert fifo_time < 5.0  # Should complete within 5 seconds

    @pytest.mark.asyncio
    async def test_decimal_precision_performance(self, test_db):
        """Test performance with high precision decimals."""
        # Create lots with high precision
        start_time = time.time()
        
        for i in range(1000):
            lot = TaxLot(
                user_id=123,
                security_id=1,
                open_date=datetime(2024, 1, 1, 10, 0, 0) + timedelta(days=i),
                open_qty=Decimal("100.123456789"),
                remaining_qty=Decimal("100.123456789"),
                open_price=Decimal("150.987654321"),
                charges=Decimal("5.123456789"),
                status=LotStatus.OPEN
            )
            test_db.add(lot)
        
        await test_db.commit()
        precision_time = time.time() - start_time
        
        print(f"Created 1000 high-precision lots in {precision_time:.2f} seconds")
        assert precision_time < 5.0  # Should complete within 5 seconds
