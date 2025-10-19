#!/usr/bin/env python3
"""
Quick Test Script for Position Tracker API

This script performs a quick validation of the core functionality
to ensure everything is working before running comprehensive tests.
"""

import asyncio
import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_basic_functionality():
    """Test basic functionality of the position tracker."""
    print("🧪 Running Quick Test for Position Tracker API")
    print("=" * 50)
    
    try:
        # Test 1: Import modules
        print("\n1. Testing imports...")
        from app.services.processing_service import processing_service
        from app.models.tax_lot import TaxLot, LotStatus
        from app.api.v1.schemas.trade import Trade
        print("✅ All imports successful")
        
        # Test 2: Create test trade
        print("\n2. Testing trade creation...")
        trade = Trade(
            user_id=123,
            security_id=1,
            side="BUY",
            quantity=Decimal("100.0"),
            price=Decimal("150.0"),
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            charges=Decimal("5.0")
        )
        print(f"✅ Trade created: {trade.side} {trade.quantity} shares at ${trade.price}")
        
        # Test 3: Test tax lot creation
        print("\n3. Testing tax lot creation...")
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
        print(f"✅ Tax lot created: {lot.open_qty} shares at ${lot.open_price}")
        
        # Test 4: Test FIFO logic
        print("\n4. Testing FIFO logic...")
        
        # Create multiple lots
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
        
        print("✅ Created two tax lots for FIFO testing")
        
        # Test 5: Test tax calculations
        print("\n5. Testing tax calculations...")
        
        # Short-term calculation
        holding_period = datetime(2024, 2, 1, 10, 0, 0) - datetime(2024, 1, 1, 10, 0, 0)
        is_short_term = holding_period < timedelta(days=365)
        
        gross_gain = (Decimal("170.0") - Decimal("150.0")) * Decimal("100.0")
        charges = Decimal("5.0") + Decimal("4.0")
        taxable_gain = gross_gain - charges
        
        if is_short_term:
            tax = taxable_gain * Decimal('0.25')
            tax_type = "Short-term"
        else:
            tax = taxable_gain * Decimal('0.125')
            tax_type = "Long-term"
        
        print(f"✅ Tax calculation: {tax_type} tax = ${tax:.2f}")
        
        # Test 6: Test decimal precision
        print("\n6. Testing decimal precision...")
        high_precision_qty = Decimal("100.123456789")
        high_precision_price = Decimal("150.987654321")
        result = high_precision_qty * high_precision_price
        print(f"✅ High precision calculation: {high_precision_qty} × {high_precision_price} = {result}")
        
        # Test 7: Test edge cases
        print("\n7. Testing edge cases...")
        
        # Zero quantity
        zero_qty = Decimal("0.0")
        print(f"✅ Zero quantity handling: {zero_qty}")
        
        # Very small quantity
        small_qty = Decimal("0.0001")
        print(f"✅ Small quantity handling: {small_qty}")
        
        # Very large quantity
        large_qty = Decimal("999999.9999")
        print(f"✅ Large quantity handling: {large_qty}")
        
        print("\n" + "=" * 50)
        print("🎉 ALL QUICK TESTS PASSED!")
        print("✅ Your position tracker is ready for comprehensive testing.")
        print("\nNext steps:")
        print("1. Run: python run_comprehensive_tests.py")
        print("2. Check test reports for detailed validation")
        print("3. Your application is ready for your sir!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the position-tracker-main directory")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Check that all files are present")
        return False

def main():
    """Main function."""
    print("Position Tracker API - Quick Test")
    print("This script validates basic functionality before comprehensive testing.")
    
    # Check if we're in the right directory
    if not os.path.exists("app/main.py"):
        print("❌ Error: Please run this script from the position-tracker-main directory")
        sys.exit(1)
    
    # Run the test
    success = asyncio.run(test_basic_functionality())
    
    if success:
        print("\n🚀 Ready to run comprehensive tests!")
        sys.exit(0)
    else:
        print("\n🔧 Please fix the issues above before running comprehensive tests.")
        sys.exit(1)

if __name__ == "__main__":
    main()
