# 🚀 Quick Test Guide - Position Tracker API

## **Test Setup**
- **User ID**: `5001`
- **Security IDs**: `501`, `502`
- **All data is fresh and unique** ✨

---

## **Step 1: Start Docker**
```bash
docker-compose up -d
```

Wait for all services to be healthy (check: `docker-compose ps`)

---

## **Step 2: Set Initial Prices**

**Endpoint**: `POST http://localhost:8000/api/v1/simulate/prices`

**Request Body** (copy-paste):
```json
{
  "updates": [
    {
      "security_id": 501,
      "price": 150.00
    },
    {
      "security_id": 502,
      "price": 76.00
    }
  ]
}
```

---

## **Step 3: Buy Trades - Security 501**

**Endpoint**: `POST http://localhost:8000/api/v1/simulate/trades`

### **Trade 1 - First Buy**
```json
{
  "user_id": 5001,
  "security_id": 501,
  "side": "BUY",
  "quantity": 200,
  "price": 145.75,
  "timestamp": "2024-09-01T09:00:00",
  "charges": 10.00
}
```

### **Trade 2 - Second Buy**
```json
{
  "user_id": 5001,
  "security_id": 501,
  "side": "BUY",
  "quantity": 150,
  "price": 152.25,
  "timestamp": "2024-09-10T11:30:00",
  "charges": 7.50
}
```

### **Trade 3 - Third Buy**
```json
{
  "user_id": 5001,
  "security_id": 501,
  "side": "BUY",
  "quantity": 100,
  "price": 155.00,
  "timestamp": "2024-09-20T14:15:00",
  "charges": 5.00
}
```

**Expected**: You now have 450 units at average cost ~150.33

---

## **Step 4: Check Portfolio**

**Endpoint**: `GET http://localhost:8000/api/v1/portfolios/5001/snapshot`

**Expected Output**: 
- Quantity: 450
- Average Cost Basis: ~150.33
- Market Value: Current Price × 450
- Unrealized P&L: (Current Price - ~150.33) × 450

---

## **Step 5: View Tax Lots**

**Endpoint**: `GET http://localhost:8000/api/v1/taxlots/?user_id=5001&security_id=501`

**Expected Output**: 
- 3 open lots (one per buy)
- Lot 1: 200 units @ $145.75
- Lot 2: 150 units @ $152.25
- Lot 3: 100 units @ $155.00

---

## **Step 6: Update Price (Simulate Market Movement)**

**Endpoint**: `POST http://localhost:8000/api/v1/simulate/prices`

```json
{
  "updates": [
    {
      "security_id": 501,
      "price": 165.00
    }
  ]
}
```

**Expected**: Portfolio unrealized P&L increases (if you have long positions)

---

## **Step 7: Sell Trade (FIFO Processing)**

**Endpoint**: `POST http://localhost:8000/api/v1/simulate/trades`

```json
{
  "user_id": 5001,
  "security_id": 501,
  "side": "SELL",
  "quantity": 200,
  "timestamp": "2024-09-25T10:00:00",
  "charges": 10.00
}
```

**Expected**: 
- FIFO: Sells from oldest lot first (Lot 1: 200 @ $145.75)
- Realized P&L: ~(165 - 145.75) × 200 - 10 = ~$3830
- Short-term capital gains calculated

---

## **Step 8: Trade Different Security (502)**

**Endpoint**: `POST http://localhost:8000/api/v1/simulate/trades`

```json
{
  "user_id": 5001,
  "security_id": 502,
  "side": "BUY",
  "quantity": 300,
  "price": 75.25,
  "timestamp": "2024-08-20T08:00:00",
  "charges": 15.00
}
```

---

## **Step 9: Update Price for Security 502**

**Endpoint**: `POST http://localhost:8000/api/v1/simulate/prices`

```json
{
  "updates": [
    {
      "security_id": 502,
      "price": 82.50
    }
  ]
}
```

---

## **Step 10: Sell Security 502**

**Endpoint**: `POST http://localhost:8000/api/v1/simulate/trades`

```json
{
  "user_id": 5001,
  "security_id": 502,
  "side": "SELL",
  "quantity": 150,
  "timestamp": "2024-10-01T09:00:00",
  "charges": 7.50
}
```

**Expected**: 
- FIFO: Sells from oldest lot (150 units @ $75.25)
- Realized P&L: ~(82.50 - 75.25) × 150 - 7.50 = ~$1080
- Short-term gains

---

## **Step 11: Final Portfolio Check**

**Endpoint**: `GET http://localhost:8000/api/v1/portfolios/5001/snapshot`

**Expected**:
- Security 501: 250 units remaining (from original 450, sold 200)
- Security 502: 150 units remaining (from original 300, sold 150)
- Realized P&L: Combined from all sales
- Unrealized P&L: Based on current market prices

---

## **Step 12: View All Tax Lots**

**Endpoint**: `GET http://localhost:8000/api/v1/taxlots/?user_id=5001`

**Expected Output**: See all open and closed lots for user 5001

---

## **Step 13: Test Event Master Integration**

**Endpoint**: `GET http://localhost:8000/api/v1/taxlots/event-master/501`

**Expected Output**: 
- All open/partial lots for security 501
- Summary statistics
- Details of each lot

---

## **Step 14: Trade Another Security (503)**

**Endpoint**: `POST http://localhost:8000/api/v1/simulate/trades`

```json
{
  "user_id": 5001,
  "security_id": 503,
  "side": "BUY",
  "quantity": 500,
  "price": 42.50,
  "timestamp": "2024-07-15T10:00:00",
  "charges": 25.00
}
```

Set price: `POST http://localhost:8000/api/v1/simulate/prices`
```json
{
  "updates": [
    {
      "security_id": 503,
      "price": 48.75
    }
  ]
}
```

---

## **Step 15: Long-Term Tax Test**

**Sell after 365+ days for long-term tax**
```json
{
  "user_id": 5001,
  "security_id": 503,
  "side": "SELL",
  "quantity": 200,
  "timestamp": "2025-07-16T10:00:00",
  "charges": 10.00
}
```

**Expected**: 
- Long-term capital gains (12.5% tax rate)
- Different from short-term (25% tax rate)

---

## **🎯 Test Results to Verify**

✅ **FIFO Processing**: Oldest lots sold first
✅ **Tax Lots**: Properly created and updated
✅ **Portfolio Snapshot**: Accurate quantities and averages
✅ **Unrealized P&L**: Calculated based on current prices
✅ **Realized P&L**: Calculated on sales
✅ **Tax Calculations**: Short-term vs Long-term
✅ **Multiple Securities**: Different securities tracked separately
✅ **Price Updates**: Market changes reflected properly

---

## **📊 Quick Verification Commands**

```bash
# Check API health
curl http://localhost:8000/health

# Get portfolio snapshot
curl http://localhost:8000/api/v1/portfolios/5001/snapshot

# Get tax lots
curl http://localhost:8000/api/v1/taxlots/?user_id=5001

# Test event master
curl http://localhost:8000/api/v1/taxlots/event-master/501
```

---

## **🔥 Tips**

1. Use **Swagger UI**: `http://localhost:8000/docs` for interactive testing
2. Monitor **Docker logs**: `docker-compose logs -f api`
3. Check **Database**: `docker-compose exec postgres psql -U tracker_user -d position_tracker`
4. Verify **tax calculations** manually for accuracy

---

**Happy Testing! 🚀**
