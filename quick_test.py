import requests
import json

BASE_URL = "http://localhost:8000"

# Test 1: Set price
print("Test 1: Setting price...")
try:
    payload = {
        "security_id": 999,
        "price": 100.0
    }
    print(f"Sending: {json.dumps(payload)}")
    response = requests.post(f"{BASE_URL}/api/v1/simulate/prices", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 2: BUY
print("Test 2: BUY trade...")
response = requests.post(f"{BASE_URL}/api/v1/simulate/trades", json={
    "user_id": 8888,
    "security_id": 999,
    "side": "BUY",
    "quantity": 10,
    "price": 100.0,
    "timestamp": "2024-01-01T10:00:00",
    "charges": 1.0
})
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
print()

# Test 3: Update price
print("Test 3: Update price...")
response = requests.post(f"{BASE_URL}/api/v1/simulate/prices", json={
    "security_id": 999,
    "price": 120.0
})
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
print()

# Test 4: SELL
print("Test 4: SELL trade...")
response = requests.post(f"{BASE_URL}/api/v1/simulate/trades", json={
    "user_id": 8888,
    "security_id": 999,
    "side": "SELL",
    "quantity": 5,
    "timestamp": "2024-01-02T10:00:00",
    "charges": 1.0
})
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
print()

# Test 5: Get tax lots
print("Test 5: Get tax lots...")
response = requests.get(f"{BASE_URL}/api/v1/taxlots/?user_id=8888&security_id=999")
print(f"Status: {response.status_code}")
print(f"Tax lots: {len(response.json())}")
for lot in response.json():
    print(f"  Lot: status={lot.get('status')}, remaining={lot.get('remaining_qty')}")
