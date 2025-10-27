# Event Master Integration

This document describes the integration between the Event Master system and the Position Tracker API.

## 🎯 Overview

When an event occurs for a specific security in the Event Master system, it needs to retrieve information about all open and partial positions for that security from the Position Tracker.

## 🔗 API Endpoint

### **GET /api/v1/taxlots/event-master/{security_id}**

**Purpose**: Retrieve all open and partial lots for a specific security across all users.

**Parameters**:
- `security_id` (path): The security ID for which the event occurred

**Response**:
```json
{
  "security_id": 501,
  "total_open_lots": 5,
  "total_remaining_qty": 675.0,
  "total_users_affected": 3,
  "lots": [
    {
      "user_id": 1001,
      "security_id": 501,
      "open_qty": 100.0,
      "remaining_qty": 25.0,
      "open_price": 150.0,
      "open_date": "2024-01-01T10:00:00",
      "status": "PARTIAL"
    },
    {
      "user_id": 1002,
      "security_id": 501,
      "open_qty": 200.0,
      "remaining_qty": 200.0,
      "open_price": 160.0,
      "open_date": "2024-01-10T10:00:00",
      "status": "OPEN"
    }
  ]
}
```

## 📊 Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `security_id` | int | The security that triggered the event |
| `total_open_lots` | int | Number of open/partial lots |
| `total_remaining_qty` | float | Total remaining quantity across all lots |
| `total_users_affected` | int | Number of unique users with open positions |
| `lots` | array | List of individual lot details |

### Lot Details

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | int | User who owns this lot |
| `security_id` | int | Security ID |
| `open_qty` | float | Original quantity purchased |
| `remaining_qty` | float | Current remaining quantity |
| `open_price` | float | Price at which the lot was purchased |
| `open_date` | string | Date when the lot was opened (ISO format) |
| `status` | string | Lot status: "OPEN" or "PARTIAL" |

## 🚀 Usage Examples

### **Example 1: Event occurs for Security 501**

```bash
curl -X GET "http://localhost:8000/api/v1/taxlots/event-master/501"
```

**Response**:
```json
{
  "security_id": 501,
  "total_open_lots": 3,
  "total_remaining_qty": 425.0,
  "total_users_affected": 2,
  "lots": [
    {
      "user_id": 1001,
      "security_id": 501,
      "open_qty": 100.0,
      "remaining_qty": 25.0,
      "open_price": 150.0,
      "open_date": "2024-01-01T10:00:00",
      "status": "PARTIAL"
    },
    {
      "user_id": 1002,
      "security_id": 501,
      "open_qty": 200.0,
      "remaining_qty": 200.0,
      "open_price": 160.0,
      "open_date": "2024-01-10T10:00:00",
      "status": "OPEN"
    },
    {
      "user_id": 1002,
      "security_id": 501,
      "open_qty": 100.0,
      "remaining_qty": 100.0,
      "open_price": 165.0,
      "open_date": "2024-01-20T10:00:00",
      "status": "OPEN"
    }
  ]
}
```

### **Example 2: No open positions for Security 999**

```bash
curl -X GET "http://localhost:8000/api/v1/taxlots/event-master/999"
```

**Response**:
```json
{
  "detail": "No open or partial lots found for security_id: 999"
}
```

## 🔄 Integration Flow

1. **Event Occurs**: Event Master detects an event for a specific security
2. **API Call**: Event Master calls the Position Tracker API
3. **Data Retrieval**: Position Tracker queries all open/partial lots for that security
4. **Response**: Position Tracker returns aggregated data about affected users
5. **Processing**: Event Master processes the data for the event

## 🧪 Testing

### **Test Script**

Run the test script to verify the integration:

```bash
python test_event_master_integration.py
```

This script will:
1. Create test data with multiple users and securities
2. Simulate events for different securities
3. Show the Event Master integration in action

### **Manual Testing**

1. **Start the server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Create some test data** (buy some stocks):
   ```bash
   curl -X POST "http://localhost:8000/api/v1/simulate/trades" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": 1001,
       "security_id": 501,
       "side": "BUY",
       "quantity": 100.0,
       "price": 150.0,
       "timestamp": "2024-01-01T10:00:00",
       "charges": 5.0
     }'
   ```

3. **Test the Event Master endpoint**:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/taxlots/event-master/501"
   ```

## 📋 Error Handling

### **404 Not Found**
- **Cause**: No open or partial lots found for the security
- **Response**: `{"detail": "No open or partial lots found for security_id: {security_id}"}`

### **500 Internal Server Error**
- **Cause**: Database connection issues or other server errors
- **Response**: Standard FastAPI error response

## 🎯 Use Cases

### **Corporate Actions**
- Stock splits, dividends, mergers
- Need to identify all holders of a specific security

### **Market Events**
- Trading halts, delistings
- Risk management for specific securities

### **Regulatory Reporting**
- Position reporting for specific securities
- Compliance checks

### **Risk Management**
- Exposure analysis for specific securities
- Portfolio impact assessment

## 🔧 Implementation Notes

- **Performance**: Query is optimized to only fetch open/partial lots
- **Scalability**: Can handle large numbers of users and lots
- **Data Integrity**: Only returns lots with `remaining_qty > 0`
- **Ordering**: Results are ordered by `open_date` (FIFO order)

## 🚀 Next Steps

1. **Authentication**: Add API key authentication for Event Master
2. **Rate Limiting**: Implement rate limiting for the endpoint
3. **Caching**: Add caching for frequently accessed securities
4. **Monitoring**: Add logging and monitoring for the integration
5. **Webhooks**: Consider webhook-based integration for real-time events

## 📞 Support

For questions or issues with the Event Master integration:
- Check the API documentation at `/docs`
- Review the test script for examples
- Check server logs for error details

