# Position Tracker API - Comprehensive Testing Guide

This guide provides comprehensive testing instructions to ensure your position tracker works perfectly under all kinds of different trade inputs and scenarios.

## 🚀 Quick Start

### 1. Prerequisites

Make sure you have the following installed:
- Python 3.10+
- pip
- All dependencies from `requirements.txt`

### 2. Install Dependencies

```bash
# Install main dependencies
pip install -r requirements.txt

# Install test dependencies
pip install -r test_requirements.txt
```

### 3. Run Quick Test

```bash
python quick_test.py
```

This will validate basic functionality and ensure everything is working.

## 🧪 Comprehensive Testing

### 1. Run All Tests

```bash
python run_comprehensive_tests.py
```

This script will:
- ✅ Run unit tests for core business logic
- ✅ Run integration tests for API endpoints
- ✅ Run performance tests with large datasets
- ✅ Run edge case tests
- ✅ Run FIFO scenario tests
- ✅ Generate comprehensive test reports
- ✅ Validate tax calculations
- ✅ Test decimal precision handling

### 2. Manual API Testing

Start the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

In another terminal, run:
```bash
python test_api_manually.py
```

This will test all API endpoints with various scenarios.

## 📊 Test Coverage

### Core Functionality Tests

1. **Buy Trade Processing**
   - Basic buy trades
   - Zero quantity trades
   - High precision quantities
   - Large quantities
   - Zero charges

2. **Sell Trade Processing (FIFO)**
   - Single lot sales
   - Multiple lot sales
   - Partial sales
   - Complete sales
   - Cross-lot sales

3. **Tax Calculations**
   - Short-term capital gains (25% tax)
   - Long-term capital gains (12.5% tax)
   - Capital losses (no tax)
   - Break-even trades
   - Charges allocation

4. **Edge Cases**
   - Zero quantities
   - Very small quantities (0.0001)
   - Very large quantities (999,999.9999)
   - Zero prices
   - Negative charges
   - Exact 365-day holding period
   - High precision decimals

### FIFO Scenarios

1. **Complex FIFO Scenarios**
   - Multiple lots with different dates
   - Mixed holding periods
   - Identical prices
   - High precision calculations
   - Very small quantities

2. **Partial Sales**
   - Single lot partial sales
   - Multiple lot partial sales
   - Cross-lot partial sales
   - High precision partial sales

### Performance Tests

1. **Large Dataset Performance**
   - 1,000+ tax lots
   - 100+ concurrent trades
   - Bulk trade processing
   - Memory usage validation

2. **Database Performance**
   - Query performance
   - Insert performance
   - Update performance
   - Transaction performance

## 🔍 Test Scenarios

### Scenario 1: Basic Trading
```
1. Buy 100 shares at $150.00
2. Buy 50 shares at $160.00
3. Update price to $175.00
4. Sell 75 shares at $170.00
5. Check portfolio snapshot
6. Verify tax lots
```

### Scenario 2: FIFO Testing
```
1. Buy 100 shares at $150.00 (Day 1)
2. Buy 200 shares at $160.00 (Day 15)
3. Buy 150 shares at $155.00 (Day 30)
4. Sell 300 shares at $170.00 (Day 45)
   - Should consume: 100 + 200 + 100 from third lot
   - First lot: CLOSED
   - Second lot: CLOSED
   - Third lot: PARTIAL (50 remaining)
```

### Scenario 3: Tax Calculations
```
1. Buy 100 shares at $150.00 (Long-term: 400 days ago)
2. Buy 200 shares at $160.00 (Short-term: 30 days ago)
3. Sell 150 shares at $170.00
   - 100 shares: Long-term tax (12.5%)
   - 50 shares: Short-term tax (25%)
```

### Scenario 4: Edge Cases
```
1. Buy 0.0001 shares at $150.00
2. Buy 999,999.9999 shares at $150.00
3. Buy 100 shares at $0.00
4. Buy 100 shares with -$5.00 charges
5. Sell after exactly 365 days
6. Sell after 364 days
```

## 📈 Expected Results

### Portfolio Snapshot
```json
{
  "summary": {
    "user_id": 123,
    "total_market_value": 17500.00,
    "total_unrealized_pnl": 2500.00,
    "realized_pnl_ytd": 1200.00,
    "stcg_ytd": 300.00,
    "ltcg_ytd": 150.00,
    "last_updated": "2024-01-15T10:30:00Z"
  },
  "positions": [
    {
      "security_id": "1",
      "quantity": 100.0000,
      "avg_cost_basis": 150.0000,
      "current_price": 175.0000,
      "market_value": 17500.0000,
      "unrealized_pnl": 2500.0000
    }
  ]
}
```

### Tax Lot Status
- **OPEN**: Lot is fully open (remaining_qty = open_qty)
- **PARTIAL**: Lot is partially closed (0 < remaining_qty < open_qty)
- **CLOSED**: Lot is fully closed (remaining_qty = 0)

### Tax Calculations
- **Short-term**: < 365 days, 25% tax rate
- **Long-term**: ≥ 365 days, 12.5% tax rate
- **Charges**: Proportionally allocated to reduce taxable gains

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure you're in the right directory
   cd position-tracker-main
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r test_requirements.txt
   ```

2. **Database Errors**
   ```bash
   # Remove old database
   rm local_test.db
   
   # Restart server
   uvicorn app.main:app --reload
   ```

3. **Test Failures**
   ```bash
   # Run specific test
   pytest tests/test_processing_service.py::TestProcessingService::test_buy_trade_processing -v
   
   # Run with more verbose output
   pytest tests/ -v -s
   ```

4. **API Connection Errors**
   ```bash
   # Check if server is running
   curl http://localhost:8000/
   
   # Start server if not running
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📋 Test Checklist

Before sending to your sir, ensure:

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All edge case tests pass
- [ ] All FIFO scenario tests pass
- [ ] All performance tests pass
- [ ] Manual API testing works
- [ ] Portfolio snapshots are accurate
- [ ] Tax calculations are correct
- [ ] Decimal precision is maintained
- [ ] Error handling works properly
- [ ] Large datasets are handled efficiently
- [ ] Concurrent operations work correctly

## 🎯 Success Criteria

Your position tracker is ready when:

1. ✅ **All tests pass** - No failing tests
2. ✅ **API responds correctly** - All endpoints work
3. ✅ **FIFO logic is accurate** - Correct lot processing
4. ✅ **Tax calculations are correct** - Proper STCG/LTCG
5. ✅ **Edge cases are handled** - No crashes on unusual inputs
6. ✅ **Performance is acceptable** - Handles large datasets
7. ✅ **Decimal precision is maintained** - No rounding errors
8. ✅ **Error handling works** - Graceful failure handling

## 📊 Test Reports

After running comprehensive tests, check:

- `test_report.html` - Detailed test results
- `htmlcov/index.html` - Code coverage report
- Console output - Real-time test results

## 🚀 Production Readiness

Once all tests pass, your position tracker is ready for:

- ✅ Production deployment
- ✅ Real-world trading scenarios
- ✅ High-volume operations
- ✅ Complex tax calculations
- ✅ Edge case handling
- ✅ Performance requirements

## 📞 Support

If you encounter any issues:

1. Check the test output for specific error messages
2. Review the troubleshooting section above
3. Ensure all dependencies are installed
4. Verify the server is running correctly
5. Check database connectivity

Your position tracker is now thoroughly tested and ready for your sir! 🎉
