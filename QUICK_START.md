# 🚀 Quick Start - Test Your API

## 1. Open Swagger UI
👉 http://localhost:8000/docs

---

## 2. Run These Tests (in order)

### Test A: Set Price First
```
POST /api/v1/simulate/prices
```
```json
{
  "security_id": 1,
  "price": 100
}
```

---

### Test B: BUY Trade
```
POST /api/v1/simulate/trades
```
```json
{
  "user_id": 1,
  "security_id": 1,
  "side": "BUY",
  "quantity": 10,
  "price": 95,
  "timestamp": "2024-01-01T10:00:00",
  "charges": 1
}
```

---

### Test C: SELL Trade (no price!)
```
POST /api/v1/simulate/trades
```
```json
{
  "user_id": 1,
  "security_id": 1,
  "side": "SELL",
  "quantity": 5,
  "timestamp": "2024-01-02T10:00:00",
  "charges": 1
}
```

---

### Test D: Check Results
```
GET /api/v1/taxlots/?user_id=1&security_id=1
```

Should show: 1 lot with 5 remaining shares

---

## ✅ What Works:

- ✅ BUY creates tax lot (price required)
- ✅ SELL uses market price automatically (no price needed!)
- ✅ FIFO sells oldest lot first
- ✅ Charges and taxes calculated

## 🎉 Success Indicators:

- All requests return 202 or 200
- No "No price data found" errors
- Tax lots show correct remaining quantities
- Portfolio calculates unrealized P&L

---

**That's it! Your API is working! 🎊**

