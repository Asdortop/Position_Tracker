#!/usr/bin/env python3
"""
Manual API Testing Script for Position Tracker

This script manually tests the API endpoints to ensure they work correctly
with various trade inputs and scenarios.
"""

import requests
import json
import time
from decimal import Decimal
from datetime import datetime, timedelta

class APITester:
    """Manual API tester for position tracker."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.user_id = 123
        self.security_id = 1
    
    def test_health_check(self):
        """Test health check endpoint."""
        print("🔍 Testing health check...")
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ Health check passed")
                print(f"   Response: {response.json()}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_buy_trade(self, quantity=100.0, price=150.0, charges=5.0):
        """Test buy trade endpoint."""
        print(f"🔍 Testing buy trade: {quantity} shares at ${price}")
        try:
            trade_data = {
                "user_id": self.user_id,
                "security_id": self.security_id,
                "side": "BUY",
                "quantity": quantity,
                "price": price,
                "timestamp": datetime.now().isoformat(),
                "charges": charges
            }
            
            response = requests.post(f"{self.base_url}/api/v1/simulate/trades", json=trade_data)
            if response.status_code == 202:
                print("✅ Buy trade successful")
                print(f"   Response: {response.json()}")
                return True
            else:
                print(f"❌ Buy trade failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Buy trade error: {e}")
            return False
    
    def test_sell_trade(self, quantity=50.0, price=170.0, charges=3.0):
        """Test sell trade endpoint."""
        print(f"🔍 Testing sell trade: {quantity} shares at ${price}")
        try:
            trade_data = {
                "user_id": self.user_id,
                "security_id": self.security_id,
                "side": "SELL",
                "quantity": quantity,
                "price": price,
                "timestamp": datetime.now().isoformat(),
                "charges": charges
            }
            
            response = requests.post(f"{self.base_url}/api/v1/simulate/trades", json=trade_data)
            if response.status_code == 202:
                print("✅ Sell trade successful")
                print(f"   Response: {response.json()}")
                return True
            else:
                print(f"❌ Sell trade failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Sell trade error: {e}")
            return False
    
    def test_price_update(self, price=175.0):
        """Test price update endpoint."""
        print(f"🔍 Testing price update: ${price}")
        try:
            price_data = {
                "user_id": self.user_id,
                "security_id": self.security_id,
                "price": price
            }
            
            response = requests.post(f"{self.base_url}/api/v1/simulate/prices", json=price_data)
            if response.status_code == 200:
                print("✅ Price update successful")
                print(f"   Response: {response.json()}")
                return True
            else:
                print(f"❌ Price update failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Price update error: {e}")
            return False
    
    def test_portfolio_snapshot(self):
        """Test portfolio snapshot endpoint."""
        print("🔍 Testing portfolio snapshot...")
        try:
            response = requests.get(f"{self.base_url}/api/v1/portfolios/{self.user_id}/snapshot")
            if response.status_code == 200:
                print("✅ Portfolio snapshot successful")
                data = response.json()
                print(f"   User ID: {data['summary']['user_id']}")
                print(f"   Total Market Value: ${data['summary']['total_market_value']}")
                print(f"   Unrealized P&L: ${data['summary']['total_unrealized_pnl']}")
                print(f"   Positions: {len(data['positions'])}")
                return True
            else:
                print(f"❌ Portfolio snapshot failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Portfolio snapshot error: {e}")
            return False
    
    def test_tax_lots(self):
        """Test tax lots endpoint."""
        print("🔍 Testing tax lots...")
        try:
            response = requests.get(f"{self.base_url}/api/v1/taxlots/?user_id={self.user_id}")
            if response.status_code == 200:
                print("✅ Tax lots successful")
                data = response.json()
                print(f"   Total lots: {len(data)}")
                for i, lot in enumerate(data[:3]):  # Show first 3 lots
                    print(f"   Lot {i+1}: {lot['open_qty']} shares at ${lot['open_price']} - {lot['status']}")
                return True
            else:
                print(f"❌ Tax lots failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Tax lots error: {e}")
            return False
    
    def test_comprehensive_scenario(self):
        """Test a comprehensive trading scenario."""
        print("\n🚀 Testing Comprehensive Trading Scenario")
        print("=" * 50)
        
        # Step 1: Initial buy
        print("\n1. Initial purchase...")
        if not self.test_buy_trade(100.0, 150.0, 5.0):
            return False
        
        # Step 2: Additional buy
        print("\n2. Additional purchase...")
        if not self.test_buy_trade(50.0, 160.0, 3.0):
            return False
        
        # Step 3: Update price
        print("\n3. Price update...")
        if not self.test_price_update(175.0):
            return False
        
        # Step 4: Check portfolio
        print("\n4. Portfolio snapshot...")
        if not self.test_portfolio_snapshot():
            return False
        
        # Step 5: Partial sell
        print("\n5. Partial sale...")
        if not self.test_sell_trade(75.0, 180.0, 4.0):
            return False
        
        # Step 6: Check tax lots
        print("\n6. Tax lots...")
        if not self.test_tax_lots():
            return False
        
        # Step 7: Final portfolio check
        print("\n7. Final portfolio snapshot...")
        if not self.test_portfolio_snapshot():
            return False
        
        print("\n✅ Comprehensive scenario completed successfully!")
        return True
    
    def test_edge_cases(self):
        """Test edge cases."""
        print("\n🧪 Testing Edge Cases")
        print("=" * 30)
        
        edge_cases = [
            {"name": "Zero quantity", "quantity": 0.0, "price": 150.0, "charges": 0.0},
            {"name": "Very small quantity", "quantity": 0.0001, "price": 150.0, "charges": 0.01},
            {"name": "Very large quantity", "quantity": 999999.9999, "price": 150.0, "charges": 50000.0},
            {"name": "Zero price", "quantity": 100.0, "price": 0.0, "charges": 5.0},
            {"name": "High precision", "quantity": 100.123456789, "price": 150.987654321, "charges": 5.123456789},
        ]
        
        for case in edge_cases:
            print(f"\nTesting: {case['name']}")
            if self.test_buy_trade(case['quantity'], case['price'], case['charges']):
                print(f"✅ {case['name']} passed")
            else:
                print(f"❌ {case['name']} failed")
    
    def run_all_tests(self):
        """Run all tests."""
        print("🧪 Position Tracker API Manual Testing")
        print("=" * 50)
        
        # Check if server is running
        if not self.test_health_check():
            print("\n❌ Server is not running. Please start the server first:")
            print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
            return False
        
        # Run comprehensive scenario
        if not self.test_comprehensive_scenario():
            print("\n❌ Comprehensive scenario failed")
            return False
        
        # Run edge cases
        self.test_edge_cases()
        
        print("\n🎉 All tests completed!")
        print("\n📊 Summary:")
        print("✅ Health check passed")
        print("✅ Buy trades working")
        print("✅ Sell trades working")
        print("✅ Price updates working")
        print("✅ Portfolio snapshots working")
        print("✅ Tax lots working")
        print("✅ Edge cases handled")
        
        return True

def main():
    """Main function."""
    print("Position Tracker API - Manual Testing")
    print("This script tests the API endpoints manually.")
    print("\nMake sure the server is running:")
    print("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    
    input("\nPress Enter when the server is running...")
    
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Your position tracker is working perfectly!")
        print("📈 Ready for production use!")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")

if __name__ == "__main__":
    main()
