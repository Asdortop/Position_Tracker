# Simple Test - Copy & Paste Ready

## 📋 Complete Test Sequence (Copy One at a Time)

### 1️⃣ Set Price
```json
{
  "security_id": 500,
  "price": 100.00
}
```

### 2️⃣ BUY (100 shares)
```json
{
  "user_id": 100,
  "security_id": 500,
  "side": "BUY",
  "quantity": 100,
  "price": 95.00,
  "timestamp": "2024-01-01T09:00:00",
  "charges": 5.00
}
```

### 3️⃣ BUY (50 shares at different price)
```json
{
  "user_id": 100,
  "security_id": 500,
  "side": "BUY",
  "quantity": 50,
  "price": 105.00,
  "timestamp": "2024-01-02T09:00:00",
  "charges": 3.00
}
```

### 4️⃣ Update Price
```json
{
  "security_id": 500,
  "price": 110.00
}
```

### 5️⃣ SELL (no price field!)
```json
{
  "user_id": 100,
  "security_id": 500,
  "side": "SELL",
  "quantity": 75,
  "timestamp": "2024-01-03T09:00:00",
  "charges": 4.00
}
```

### 6️⃣ View Tax Lots
Go to: `GET /api/v1/taxlots/?user_id=100&security_id=500`

### 7️⃣ View Portfolio
Go to: `GET /api/v1/portfolios/100/snapshot`

---

## 🎯 What to Expect

**After SELL:**
- First lot (100 @ $95): Remaining = 25 shares
- Second lot (50 @ $105): Remaining = 50 shares  
- Total remaining = 75 shares
- Realized P&L calculated on 75 shares sold

**After Portfolio Check:**
- 75 remaining shares
- Weighted average cost: ~$98.33
- Market value at $110: $8,250
- Unrealized P&L: ~$875 (75 × ($110 - $98.33))

---

## 🔑 Key Points

- ✅ SELL doesn't need price field
- ✅ Price field automatically filled from market data
- ✅ FIFO sells oldest lots first
- ✅ Taxes calculated automatically

