# Quick Manual Trade Test
Copy-paste these requests into Swagger UI at: **http://localhost:8000/docs**

---

## Step 1: Set Initial Price
**Endpoint:** `POST /api/v1/simulate/prices`

```json
{
  "security_id": 500,
  "price": 150.00
}
```

**Expected Response:**
```json
{
  "message": "Price for security 500 updated to 150.00."
}
```

---

## Step 2: BUY 100 Shares
**Endpoint:** `POST /api/v1/simulate/trades`

```json
{
  "user_id": 100,
  "security_id": 500,
  "side": "BUY",
  "quantity": 100,
  "price": 145.00,
  "timestamp": "2024-01-01T10:00:00",
  "charges": 5.00
}
```

**Expected:** ✅ Status 202 - Trade accepted

---

## Step 3: BUY Another 50 Shares at Higher Price
```json
{
  "user_id": 100,
  "security_id": 500,
  "side": "BUY",
  "quantity": 50,
  "price": 155.00,
  "timestamp": "2024-01-02T10:00:00",
  "charges": 3.00
}
```

**Expected:** ✅ Status 202 - Trade accepted

---

## Step 4: Update Market Price
**Endpoint:** `POST /api/v1/simulate/prices`

```json
{
  "security_id": 500,
  "price": 165.00
}
```

**Expected:** ✅ Price updated

---

## Step 5: SELL 60 Shares (uses market price automatically)
**Endpoint:** `POST /api/v1/simulate/trades`

```json
{
  "user_id": 100,
  "security_id": 500,
  "side": "SELL",
  "quantity": 60,
  "timestamp": "2024-01-03T10:00:00",
  "charges": 3.00
}
```

**Expected:** ✅ Status 202 - Uses $165.00 as sell price (FIFO - sells oldest lot first)

---

## Step 6: Check Tax Lots
**Endpoint:** `GET /api/v1/taxlots/?user_id=100&security_id=500`

**Expected:** Shows 2 lots:
- Lot 1: 40 remaining (out of 100) - OPEN
- Lot 2: 50 remaining - OPEN

---

## Step 7: Check Portfolio
**Endpoint:** `GET /api/v1/portfolios/100/snapshot`

**Expected:** 
- Total quantity: 90 shares
- Current price: $165.00
- Market value: ~$14,850
- Unrealized P&L: Positive (based on price difference)

---

## Step 8: Final SELL (All Remaining)
```json
{
  "user_id": 100,
  "security_id": 500,
  "side": "SELL",
  "quantity": 90,
  "timestamp": "2024-01-04T10:00:00",
  "charges": 5.00
}
```

**Expected:** ✅ All remaining shares sold, lots marked CLOSED

---

## Test Results Summary

✅ **What You Should See:**

1. **BUY trades create tax lots** with different purchase prices
2. **SELL trades use market price** automatically (no price needed in request)
3. **FIFO logic** - oldest lot sells first
4. **Tax lots show remaining quantities** after partial sells
5. **Portfolio shows** unrealized P&L based on current prices
6. **All lots marked CLOSED** after final sell

---

## Notes

- ⚠️ **Price is optional for SELL** - uses current market price
- ✅ **Price is required for BUY** - must specify purchase price
- 🔄 **First lot sells first** - FIFO order
- 💰 **Taxes calculated** - 25% for short-term (<1 year), 12.5% for long-term

---

## Troubleshooting

**Error: "No price data found"**
→ Run Step 1 (set price) first

**Error: "Price is required for BUY"**
→ Make sure you include "price" field in BUY trades

**Error: 500 Internal Server Error**
→ Restart server and try again

---

**Happy Testing! 🚀**

