"""
Comprehensive Test Suite for Position Tracker API
Tests all major features: BUY, SELL, Price Updates, Portfolio, Tax Lots
"""

import requests
import json
from decimal import Decimal
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}[PASS] {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}[FAIL] {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}[INFO] {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARN] {message}{Colors.END}")

def print_header(message):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{message}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

def test_endpoint(method, url, data=None, expected_status=200):
    """Test an endpoint and return response"""
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            return None, f"Unsupported method: {method}"
        
        return response, None
    except Exception as e:
        return None, str(e)

def main():
    print_header("Position Tracker API - Comprehensive Feature Test")
    
    test_user_id = 8888
    test_security_id = 999
    
    results = {
        "passed": 0,
        "failed": 0,
        "warnings": 0
    }
    
    # Test 1: Health Check
    print_info("Test 1: Health Check")
    print(f"Testing against: {BASE_URL}")
    response, error = test_endpoint("GET", f"{BASE_URL.replace('/api/v1', '')}/health")
    if error:
        print_error(f"Health check failed: {error}")
        results["failed"] += 1
        return
    elif response.status_code == 200:
        print_success("API is running")
        results["passed"] += 1
    else:
        print_warning("Health check returned unexpected status")
        results["warnings"] += 1
    
    # Test 2: Set Initial Price
    print_info(f"\nTest 2: Setting initial price for security {test_security_id}")
    price_data = {
        "security_id": test_security_id,
        "price": 100.00
    }
    response, error = test_endpoint("POST", f"{BASE_URL}/simulate/prices", price_data)
    if error:
        print_error(f"Failed to set price: {error}")
        results["failed"] += 1
        return
    elif response.status_code == 200:
        print_success(f"Price set to $100.00")
        results["passed"] += 1
    else:
        print_error(f"Failed to set price. Status: {response.status_code}")
        results["failed"] += 1
    
    # Test 3: BUY Trade
    print_info(f"\nTest 3: BUY 100 shares at $100.00")
    buy_trade = {
        "user_id": test_user_id,
        "security_id": test_security_id,
        "side": "BUY",
        "quantity": 100,
        "price": 100.00,
        "timestamp": "2024-01-01T10:00:00",
        "charges": 5.00
    }
    response, error = test_endpoint("POST", f"{BASE_URL}/simulate/trades", buy_trade, 202)
    if error:
        print_error(f"BUY trade failed: {error}")
        results["failed"] += 1
    elif response.status_code == 202:
        print_success("BUY trade accepted")
        results["passed"] += 1
    else:
        print_error(f"BUY trade failed. Status: {response.status_code}")
        print_error(f"Response: {response.text}")
        results["failed"] += 1
    
    # Test 4: Second BUY at Different Price
    print_info(f"\nTest 4: BUY 50 shares at $110.00")
    buy_trade2 = {
        "user_id": test_user_id,
        "security_id": test_security_id,
        "side": "BUY",
        "quantity": 50,
        "price": 110.00,
        "timestamp": "2024-01-02T10:00:00",
        "charges": 3.00
    }
    response, error = test_endpoint("POST", f"{BASE_URL}/simulate/trades", buy_trade2, 202)
    if error or response.status_code != 202:
        print_warning(f"Second BUY failed")
        results["warnings"] += 1
    else:
        print_success("Second BUY trade accepted")
        results["passed"] += 1
    
    # Test 5: Update Price
    print_info(f"\nTest 5: Update price to $120.00")
    new_price = {
        "security_id": test_security_id,
        "price": 120.00
    }
    response, error = test_endpoint("POST", f"{BASE_URL}/simulate/prices", new_price)
    if error or response.status_code != 200:
        print_warning(f"Price update failed")
        results["warnings"] += 1
    else:
        print_success("Price updated to $120.00")
        results["passed"] += 1
    
    # Test 6: SELL Trade (without price - should use market price)
    print_info(f"\nTest 6: SELL 60 shares at market price ($120.00)")
    sell_trade = {
        "user_id": test_user_id,
        "security_id": test_security_id,
        "side": "SELL",
        "quantity": 60,
        "timestamp": "2024-01-03T10:00:00",
        "charges": 3.00
    }
    response, error = test_endpoint("POST", f"{BASE_URL}/simulate/trades", sell_trade, 202)
    if error:
        print_error(f"SELL trade failed: {error}")
        results["failed"] += 1
    elif response.status_code == 202:
        print_success("SELL trade accepted (uses market price)")
        results["passed"] += 1
    else:
        print_error(f"SELL trade failed. Status: {response.status_code}")
        print_error(f"Response: {response.text}")
        results["failed"] += 1
    
    # Test 7: Portfolio Snapshot
    print_info(f"\nTest 7: Get portfolio snapshot")
    response, error = test_endpoint("GET", f"{BASE_URL}/portfolios/{test_user_id}/snapshot")
    if error:
        print_error(f"Failed to get portfolio: {error}")
        results["failed"] += 1
    elif response.status_code == 200:
        data = response.json()
        print_success(f"Portfolio snapshot retrieved")
        print(f"   Total Market Value: ${data['summary']['total_market_value']}")
        print(f"   Total Unrealized P&L: ${data['summary']['total_unrealized_pnl']}")
        results["passed"] += 1
    else:
        print_error(f"Portfolio query failed. Status: {response.status_code}")
        results["failed"] += 1
    
    # Test 8: Tax Lots Query
    print_info(f"\nTest 8: Get tax lots")
    response, error = test_endpoint("GET", f"{BASE_URL}/taxlots/?user_id={test_user_id}&security_id={test_security_id}")
    if error:
        print_error(f"Failed to get tax lots: {error}")
        results["failed"] += 1
    elif response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved {len(data)} tax lot(s)")
        for i, lot in enumerate(data, 1):
            status = lot.get('status', 'Unknown')
            remaining = lot.get('remaining_qty', 0)
            realized_pnl = lot.get('realized_pnl', 0)
            print(f"   Lot {i}: Status={status}, Remaining={remaining}, Realized P&L=${realized_pnl}")
        results["passed"] += 1
    else:
        print_warning(f"Tax lots query returned status: {response.status_code}")
        results["warnings"] += 1
    
    # Test 9: SELL All Remaining Shares
    print_info(f"\nTest 9: SELL all remaining shares")
    final_sell = {
        "user_id": test_user_id,
        "security_id": test_security_id,
        "side": "SELL",
        "quantity": 90,  # Should sell remaining 90 shares
        "timestamp": "2024-01-04T10:00:00",
        "charges": 5.00
    }
    response, error = test_endpoint("POST", f"{BASE_URL}/simulate/trades", final_sell, 202)
    if error or response.status_code != 202:
        print_warning(f"Final SELL failed")
        results["warnings"] += 1
    else:
        print_success("Final SELL trade accepted")
        results["passed"] += 1
    
    # Test 10: Verify All Lots Are Closed
    print_info(f"\nTest 10: Verify all tax lots are closed")
    response, error = test_endpoint("GET", f"{BASE_URL}/taxlots/?user_id={test_user_id}&security_id={test_security_id}")
    if not error and response.status_code == 200:
        data = response.json()
        all_closed = all(lot.get('status') == 'CLOSED' for lot in data)
        if all_closed:
            print_success("All tax lots are CLOSED")
            results["passed"] += 1
        else:
            print_warning("Some lots are not CLOSED")
            results["warnings"] += 1
    
    # Summary
    print_header("Test Summary")
    print(f"[PASS] Passed: {results['passed']}")
    print(f"[FAIL] Failed: {results['failed']}")
    print(f"[WARN] Warnings: {results['warnings']}")
    
    if results['failed'] == 0:
        print_success("\n*** All critical tests passed! ***")
    else:
        print_error(f"\n*** {results['failed']} test(s) failed ***")
    
    total = results['passed'] + results['failed'] + results['warnings']
    success_rate = (results['passed'] / total * 100) if total > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {e}")

