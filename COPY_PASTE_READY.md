# 🎯 COPY-PASTE Ready Test Data

**Use these in Swagger UI at: http://localhost:8000/docs**

---

## ✅ **Step 1: Set Initial Prices**

**Endpoint**: `POST /api/v1/simulate/prices`

### Price for Security 501:
```json
{
  "security_id": 501,
  "price": 150.00
}
```

### Price for Security 502:
```json
{
  "security_id": 502,
  "price": 76.00
}
```

---

## ✅ **Step 2: Buy Trades - Security 501**

**Endpoint**: `POST /api/v1/simulate/trades`

### Buy Trade 1:
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

### Buy Trade 2:
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

### Buy Trade 3:
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

---

## ✅ **Step 3: Check Portfolio**

**Endpoint**: `GET /api/v1/portfolios/5001/snapshot`

**Expected**: 450 units at ~$150.33 average

---

## ✅ **Step 4: Update Price**

**Endpoint**: `POST /api/v1/simulate/prices`

```json
{
  "security_id": 501,
  "price": 165.00
}
```

---

## ✅ **Step 5: Sell Trade**

**Endpoint**: `POST /api/v1/simulate/trades`

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

**Expected**: FIFO sells oldest 200 units @ $145.75

---

## ✅ **Step 6: Trade Different Security**

**Endpoint**: `POST /api/v1/simulate/trades`

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

## ✅ **Step 7: Update Price for 502**

**Endpoint**: `POST /api/v1/simulate/prices`

```json
{
  "security_id": 502,
  "price": 82.50
}
```

---

## ✅ **Step 8: Sell Security 502**

**Endpoint**: `POST /api/v1/simulate/trades`

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

---

## ✅ **Step 9: Final Portfolio Check**

**Endpoint**: `GET /api/v1/portfolios/5001/snapshot`

**Expected**: 
- Security 501: 250 units remaining
- Security 502: 150 units remaining
- Realized P&L calculated
- Unrealized P&L based on current prices

---

## 🎯 **Quick Test Checklist**

- [ ] Set prices for securities 501 and 502
- [ ] Execute 3 buy trades for security 501
- [ ] Check portfolio - should show 450 units
- [ ] Update price to 165.00
- [ ] Execute sell trade (200 units)
- [ ] Check FIFO - should sell oldest lot
- [ ] Trade different security (502)
- [ ] Update price for 502
- [ ] Sell 150 units of 502
- [ ] Check final portfolio

---

## 📊 **Verify These Calculations**

✅ **FIFO**: Oldest lots sold first
✅ **Portfolio**: Accurate quantities and averages  
✅ **Tax Lots**: Properly created and updated
✅ **Unrealized P&L**: Based on current prices
✅ **Realized P&L**: Calculated on sales
✅ **Multiple Securities**: Tracked separately

---

**Happy Testing! 🚀**
