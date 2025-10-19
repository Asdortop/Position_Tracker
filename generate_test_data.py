#!/usr/bin/env python3
"""
Test Data Generator for Position Tracker API

This script generates comprehensive test data to validate the position tracker
under various real-world scenarios.
"""

import asyncio
import json
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict, Any

class TestDataGenerator:
    """Generates comprehensive test data for position tracker testing."""
    
    def __init__(self):
        self.user_id = 123
        self.security_id = 1
        self.base_date = datetime(2024, 1, 1, 9, 30, 0)  # Market open time
    
    def generate_basic_trades(self) -> List[Dict[str, Any]]:
        """Generate basic buy and sell trades."""
        trades = [
            {
                "user_id": self.user_id,
                "security_id": self.security_id,
                "side": "BUY",
                "quantity": 100.0,
                "price": 150.0,
                "timestamp": self.base_date.isoformat(),
                "charges": 5.0,
                "description": "Initial purchase"
            },
            {
                "user_id": self.user_id,
                "security_id": self.security_id,
                "side": "BUY",
                "quantity": 50.0,
                "price": 160.0,
                "timestamp": (self.base_date + timedelta(days=15)).isoformat(),
                "charges": 3.0,
                "description": "Additional purchase"
            },
            {
                "user_id": self.user_id,
                "security_id": self.security_id,
                "side": "SELL",
                "quantity": 75.0,
                "price": 170.0,
                "timestamp": (self.base_date + timedelta(days=30)).isoformat(),
                "charges": 4.0,
                "description": "Partial sale"
            }
        ]
        return trades
    
    def generate_fifo_scenarios(self) -> List[Dict[str, Any]]:
        """Generate FIFO test scenarios."""
        scenarios = []
        
        # Scenario 1: Multiple lots, single sell
        scenario1 = {
            "name": "Multiple lots, single sell",
            "trades": [
                {"side": "BUY", "quantity": 100.0, "price": 150.0, "days_offset": 0, "charges": 5.0},
                {"side": "BUY", "quantity": 200.0, "price": 160.0, "days_offset": 15, "charges": 8.0},
                {"side": "BUY", "quantity": 150.0, "price": 155.0, "days_offset": 30, "charges": 6.0},
                {"side": "SELL", "quantity": 300.0, "price": 170.0, "days_offset": 45, "charges": 12.0},
            ]
        }
        scenarios.append(scenario1)
        
        # Scenario 2: Small quantities, high precision
        scenario2 = {
            "name": "High precision quantities",
            "trades": [
                {"side": "BUY", "quantity": 100.123456789, "price": 150.987654321, "days_offset": 0, "charges": 5.123456789},
                {"side": "BUY", "quantity": 200.987654321, "price": 160.123456789, "days_offset": 10, "charges": 8.987654321},
                {"side": "SELL", "quantity": 150.5, "price": 170.5, "days_offset": 20, "charges": 10.5},
            ]
        }
        scenarios.append(scenario2)
        
        # Scenario 3: Mixed holding periods
        scenario3 = {
            "name": "Mixed holding periods",
            "trades": [
                {"side": "BUY", "quantity": 100.0, "price": 150.0, "days_offset": -400, "charges": 5.0},  # Long-term
                {"side": "BUY", "quantity": 200.0, "price": 160.0, "days_offset": 0, "charges": 8.0},      # Short-term
                {"side": "SELL", "quantity": 150.0, "price": 170.0, "days_offset": 30, "charges": 10.0},
            ]
        }
        scenarios.append(scenario3)
        
        return scenarios
    
    def generate_edge_cases(self) -> List[Dict[str, Any]]:
        """Generate edge case scenarios."""
        edge_cases = [
            {
                "name": "Zero quantity trade",
                "trades": [
                    {"side": "BUY", "quantity": 0.0, "price": 150.0, "days_offset": 0, "charges": 0.0}
                ]
            },
            {
                "name": "Very small quantities",
                "trades": [
                    {"side": "BUY", "quantity": 0.0001, "price": 150.0, "days_offset": 0, "charges": 0.01},
                    {"side": "SELL", "quantity": 0.00005, "price": 160.0, "days_offset": 10, "charges": 0.01},
                ]
            },
            {
                "name": "Very large quantities",
                "trades": [
                    {"side": "BUY", "quantity": 999999.9999, "price": 150.0, "days_offset": 0, "charges": 50000.0},
                    {"side": "SELL", "quantity": 500000.0, "price": 160.0, "days_offset": 30, "charges": 25000.0},
                ]
            },
            {
                "name": "Zero price trade",
                "trades": [
                    {"side": "BUY", "quantity": 100.0, "price": 0.0, "days_offset": 0, "charges": 5.0}
                ]
            },
            {
                "name": "Negative charges (should be treated as zero)",
                "trades": [
                    {"side": "BUY", "quantity": 100.0, "price": 150.0, "days_offset": 0, "charges": -5.0}
                ]
            },
            {
                "name": "Exact 365-day holding period",
                "trades": [
                    {"side": "BUY", "quantity": 100.0, "price": 150.0, "days_offset": -365, "charges": 5.0},
                    {"side": "SELL", "quantity": 100.0, "price": 170.0, "days_offset": 0, "charges": 5.0},
                ]
            },
            {
                "name": "364-day holding period",
                "trades": [
                    {"side": "BUY", "quantity": 100.0, "price": 150.0, "days_offset": -364, "charges": 5.0},
                    {"side": "SELL", "quantity": 100.0, "price": 170.0, "days_offset": 0, "charges": 5.0},
                ]
            },
        ]
        return edge_cases
    
    def generate_tax_scenarios(self) -> List[Dict[str, Any]]:
        """Generate tax calculation scenarios."""
        tax_scenarios = [
            {
                "name": "Short-term capital gains",
                "trades": [
                    {"side": "BUY", "quantity": 100.0, "price": 150.0, "days_offset": 0, "charges": 5.0},
                    {"side": "SELL", "quantity": 100.0, "price": 170.0, "days_offset": 30, "charges": 4.0},
                ],
                "expected_tax_type": "short_term",
                "expected_tax_rate": 0.25
            },
            {
                "name": "Long-term capital gains",
                "trades": [
                    {"side": "BUY", "quantity": 100.0, "price": 150.0, "days_offset": -400, "charges": 5.0},
                    {"side": "SELL", "quantity": 100.0, "price": 170.0, "days_offset": 0, "charges": 4.0},
                ],
                "expected_tax_type": "long_term",
                "expected_tax_rate": 0.125
            },
            {
                "name": "Capital loss",
                "trades": [
                    {"side": "BUY", "quantity": 100.0, "price": 150.0, "days_offset": 0, "charges": 5.0},
                    {"side": "SELL", "quantity": 100.0, "price": 130.0, "days_offset": 30, "charges": 4.0},
                ],
                "expected_tax_type": "loss",
                "expected_tax_rate": 0.0
            },
            {
                "name": "Break-even trade",
                "trades": [
                    {"side": "BUY", "quantity": 100.0, "price": 150.0, "days_offset": 0, "charges": 5.0},
                    {"side": "SELL", "quantity": 100.0, "price": 155.0, "days_offset": 30, "charges": 5.0},
                ],
                "expected_tax_type": "break_even",
                "expected_tax_rate": 0.0
            },
        ]
        return tax_scenarios
    
    def generate_performance_scenarios(self) -> List[Dict[str, Any]]:
        """Generate performance test scenarios."""
        performance_scenarios = [
            {
                "name": "Large dataset - 1000 lots",
                "trades": [{"side": "BUY", "quantity": 100.0, "price": 150.0, "days_offset": i, "charges": 5.0} for i in range(1000)]
            },
            {
                "name": "Bulk trades - 100 sell transactions",
                "trades": [{"side": "SELL", "quantity": 10.0, "price": 160.0, "days_offset": 30 + i, "charges": 1.0} for i in range(100)]
            },
            {
                "name": "High precision - 500 lots with 9 decimal places",
                "trades": [{"side": "BUY", "quantity": 100.123456789, "price": 150.987654321, "days_offset": i, "charges": 5.123456789} for i in range(500)]
            },
        ]
        return performance_scenarios
    
    def convert_scenario_to_trades(self, scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert a scenario to actual trade data."""
        trades = []
        for trade_data in scenario["trades"]:
            trade = {
                "user_id": self.user_id,
                "security_id": self.security_id,
                "side": trade_data["side"],
                "quantity": trade_data["quantity"],
                "price": trade_data["price"],
                "timestamp": (self.base_date + timedelta(days=trade_data["days_offset"])).isoformat(),
                "charges": trade_data["charges"],
                "scenario": scenario["name"]
            }
            trades.append(trade)
        return trades
    
    def generate_all_test_data(self) -> Dict[str, Any]:
        """Generate all test data."""
        return {
            "basic_trades": self.generate_basic_trades(),
            "fifo_scenarios": self.generate_fifo_scenarios(),
            "edge_cases": self.generate_edge_cases(),
            "tax_scenarios": self.generate_tax_scenarios(),
            "performance_scenarios": self.generate_performance_scenarios(),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "user_id": self.user_id,
                "security_id": self.security_id,
                "base_date": self.base_date.isoformat(),
                "total_scenarios": 0  # Will be calculated
            }
        }
    
    def save_test_data(self, filename: str = "test_data.json"):
        """Save test data to JSON file."""
        data = self.generate_all_test_data()
        
        # Calculate total scenarios
        total_scenarios = (
            len(data["fifo_scenarios"]) +
            len(data["edge_cases"]) +
            len(data["tax_scenarios"]) +
            len(data["performance_scenarios"])
        )
        data["metadata"]["total_scenarios"] = total_scenarios
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"✅ Test data saved to {filename}")
        print(f"📊 Generated {total_scenarios} test scenarios")
        return data

def main():
    """Main function."""
    print("🧪 Position Tracker Test Data Generator")
    print("=" * 50)
    
    generator = TestDataGenerator()
    data = generator.save_test_data()
    
    print("\n📋 Generated Test Scenarios:")
    print(f"  • Basic trades: {len(data['basic_trades'])}")
    print(f"  • FIFO scenarios: {len(data['fifo_scenarios'])}")
    print(f"  • Edge cases: {len(data['edge_cases'])}")
    print(f"  • Tax scenarios: {len(data['tax_scenarios'])}")
    print(f"  • Performance scenarios: {len(data['performance_scenarios'])}")
    
    print("\n🚀 Next steps:")
    print("1. Run: python quick_test.py")
    print("2. Run: python run_comprehensive_tests.py")
    print("3. Check test_data.json for all generated scenarios")
    
    return data

if __name__ == "__main__":
    main()
