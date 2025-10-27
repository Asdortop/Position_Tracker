# Manual Testing Guide

Use these test sequences to verify all features work correctly.

## Setup
Make sure your server is running:
```bash
uvicorn app.main:app --reload
```

Access Swagger UI: http://localhost:8000/docs

---

## Test Sequence 1: Basic BUY and SELL

### Step 1: Set Initial Price
**Endpoint:** `POST /api/v1/simulate/prices`
```json
{
  "security_id": 1001,
  "price": 150.00
}
```
**Expected:** Status 200, "Price updated..."

---

### Step 2: BUY Trade
**Endpoint:** `POST /api/v1/simulate/trades`
```json
{
  "user_id": 100,
  "security_id": 1001,
  "side": "BUY",
  "quantity": 100,
  "price": 150.00,
  "timestamp": "2024-01-01T10:00:00",
  "charges": 5.00
}
```
**Expected:** Status 202, "Trade accepted for processing"

---

### Step 3: Update Price
**Endpoint:** `POST /api/v1/simulate/prices`
```json
{
  "security_id": 1001,
  "price": 170.00
}
```

---

### Step 4: SELL Trade (without price)
**Endpoint:** `POST /api/v1/simulate/trades`
```json
{
  "user_id": 100,
  "security_id": 1001,
  "side": "SELL",
  "quantity": 50,
  "timestamp": "2024-01-02T10:00:00",
  "charges": 3.00
}
```
**Expected:** Status 202, Uses $170.00 as sell price (current market price)

---

### Step 5: Check Tax Lots
**Endpoint:** `GET /api/v1/taxlots/?user_id=100&security_id=1001`
**Expected:** Shows 1 lot with remaining_qty=50

---

### Step 6: Check Portfolio
**Endpoint:** `GET /api/v1/portfolios/100/snapshot`
**Expected:** Shows 50 remaining shares at avg cost $150.00

---

## Test Sequence 2: FIFO with Multiple Buys

### Step 1: Set Price
```json
POST /api/v1/simulate/prices
{
  "security_id": 1002,
  "price": 100.00
}
```

### Step 2: BUY 200 shares at $100
```json
POST /api/v1/simulate/trades
{
  "user_id": 200,
  "security_id": 1002,
  "side": "BUY",
  "quantity": 200,
  "price": 100.00,
  "timestamp": "2024-01-01T09:00:00",
  "charges": 10.00
}
```

### Step 3: BUY 100 shares at $110
```json
POST /api/v1/simulate/trades
{
  "user_id": 200,
  "security_id": 1002,
  "side": "BUY",
  "quantity": 100,
  "price": 110.00,
  "timestamp": "2024-01-02T09:00:00",
  "charges": 5.00
}
```

### Step 4: BUY 50 shares at $120
```json
POST /api/v1/simulate/trades
{
  "user_id": 200,
  "security_id": 1002,
  "side": "BUY",
  "quantity": 50,
  "price": 120.00,
  "timestamp": "2024-01-03T09:00:00",
  "charges": 3.00
}
```

### Step 5: Update Price to $130
```json
POST /api/v1/simulate/prices
{
  "security_id": 1002,
  "price": 130.00
}
```

### Step 6: SELL 150 shares (FIFO - should sell oldest first)
```json
POST /api/v1/simulate/trades
{
  "user_id": 200,
  "security_id": 1002,
  "side": "SELL",
  "quantity": 150,
  "timestamp": "2024-01-04T09:00:00",
  "charges": 8.00
}
```
**Expected:** 
- First lot (200 at $100): 150 sold, 50 remaining
- Realized P&L from first 150 shares

### Step 7: Verify FIFO
Check tax lots - should show:
- Lot 1: 50 remaining (out of 200)
- Lot 2: 100 remaining
- Lot 3: 50 remaining

---

## Test Sequence 3: Partial Sell Across Multiple Lots

### Set Price, Buy at multiple prices, then sell large quantity

This will test that:
- FIFO sells from multiple lots
- Charges are allocated proportionally
- Tax calculations work correctly

---

## Expected Behaviors

✅ **BUY Trade:**
- Creates new tax lot
- Price is required
- Commits to database

✅ **SELL Trade:**
- Price is optional (uses market price)
- FIFO processing
- Calculates realized P&L
- Calculates taxes (STCG 25%, LTCG 12.5%)

✅ **Price Update:**
- Updates SecurityPrice table
- Commits to database

✅ **Portfolio:**
- Calculates market value
- Shows unrealized P&L
- Aggregates by security

---

## Common Issues

**Error: "No price data found"**
→ Set price using /simulate/prices first

**Error: "Price is required for BUY trades"**
→ Make sure BUY requests include price field

**Error: Validation error**
→ Check JSON format, all required fields present

