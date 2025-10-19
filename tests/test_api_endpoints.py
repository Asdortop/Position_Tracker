import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.models.tax_lot import TaxLot, LotStatus

class TestAPIEndpoints:
    """Integration tests for API endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["service"] == "Position Tracker API"

    def test_buy_trade_endpoint(self, client):
        """Test buy trade simulation endpoint."""
        trade_data = {
            "user_id": 123,
            "security_id": 1,
            "side": "BUY",
            "quantity": 100.0,
            "price": 150.0,
            "timestamp": "2024-01-01T10:00:00Z",
            "charges": 5.0
        }
        
        response = client.post("/api/v1/simulate/trades", json=trade_data)
        assert response.status_code == 202
        assert "Trade accepted for processing" in response.json()["message"]

    def test_sell_trade_endpoint(self, client):
        """Test sell trade simulation endpoint."""
        # First create a buy trade
        buy_trade = {
            "user_id": 123,
            "security_id": 1,
            "side": "BUY",
            "quantity": 100.0,
            "price": 150.0,
            "timestamp": "2024-01-01T10:00:00Z",
            "charges": 5.0
        }
        client.post("/api/v1/simulate/trades", json=buy_trade)
        
        # Then sell
        sell_trade = {
            "user_id": 123,
            "security_id": 1,
            "side": "SELL",
            "quantity": 50.0,
            "price": 170.0,
            "timestamp": "2024-02-01T10:00:00Z",
            "charges": 3.0
        }
        
        response = client.post("/api/v1/simulate/trades", json=sell_trade)
        assert response.status_code == 202
        assert "Trade accepted for processing" in response.json()["message"]

    def test_price_update_endpoint(self, client):
        """Test price update endpoint."""
        price_data = {
            "user_id": 123,
            "security_id": 1,
            "price": 175.0
        }
        
        response = client.post("/api/v1/simulate/prices", json=price_data)
        assert response.status_code == 200
        assert "Price for 1 updated to 175.0" in response.json()["message"]

    def test_eod_taxes_endpoint(self, client):
        """Test end-of-day taxes endpoint."""
        eod_data = {
            "user_id": 123
        }
        
        response = client.post("/api/v1/simulate/eod-taxes", json=eod_data)
        assert response.status_code == 200
        assert "closed_lots_today" in response.json()

    def test_portfolio_snapshot_endpoint(self, client):
        """Test portfolio snapshot endpoint."""
        # First create some trades
        buy_trade = {
            "user_id": 123,
            "security_id": 1,
            "side": "BUY",
            "quantity": 100.0,
            "price": 150.0,
            "timestamp": "2024-01-01T10:00:00Z",
            "charges": 5.0
        }
        client.post("/api/v1/simulate/trades", json=buy_trade)
        
        # Update price
        price_data = {
            "user_id": 123,
            "security_id": 1,
            "price": 175.0
        }
        client.post("/api/v1/simulate/prices", json=price_data)
        
        # Get portfolio snapshot
        response = client.get("/api/v1/portfolios/123/snapshot")
        assert response.status_code == 200
        
        data = response.json()
        assert "summary" in data
        assert "positions" in data
        assert data["summary"]["user_id"] == 123
        assert len(data["positions"]) == 1
        
        position = data["positions"][0]
        assert position["security_id"] == "1"
        assert position["quantity"] == 100.0
        assert position["avg_cost_basis"] == 150.0
        assert position["current_price"] == 175.0
        assert position["market_value"] == 17500.0
        assert position["unrealized_pnl"] == 2500.0

    def test_tax_lots_endpoint(self, client):
        """Test tax lots listing endpoint."""
        # Create some trades
        buy_trade = {
            "user_id": 123,
            "security_id": 1,
            "side": "BUY",
            "quantity": 100.0,
            "price": 150.0,
            "timestamp": "2024-01-01T10:00:00Z",
            "charges": 5.0
        }
        client.post("/api/v1/simulate/trades", json=buy_trade)
        
        # Get tax lots
        response = client.get("/api/v1/taxlots/?user_id=123")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        
        lot = data[0]
        assert lot["user_id"] == 123
        assert lot["security_id"] == 1
        assert lot["open_qty"] == 100.0
        assert lot["remaining_qty"] == 100.0
        assert lot["status"] == "OPEN"

    def test_tax_lots_with_security_filter(self, client):
        """Test tax lots endpoint with security filter."""
        # Create trades for different securities
        buy_trade1 = {
            "user_id": 123,
            "security_id": 1,
            "side": "BUY",
            "quantity": 100.0,
            "price": 150.0,
            "timestamp": "2024-01-01T10:00:00Z",
            "charges": 5.0
        }
        
        buy_trade2 = {
            "user_id": 123,
            "security_id": 2,
            "side": "BUY",
            "quantity": 50.0,
            "price": 200.0,
            "timestamp": "2024-01-01T10:00:00Z",
            "charges": 3.0
        }
        
        client.post("/api/v1/simulate/trades", json=buy_trade1)
        client.post("/api/v1/simulate/trades", json=buy_trade2)
        
        # Get tax lots for security 1 only
        response = client.get("/api/v1/taxlots/?user_id=123&security_id=1")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["security_id"] == 1

    def test_tax_lots_with_status_filter(self, client):
        """Test tax lots endpoint with status filter."""
        # Create a buy trade
        buy_trade = {
            "user_id": 123,
            "security_id": 1,
            "side": "BUY",
            "quantity": 100.0,
            "price": 150.0,
            "timestamp": "2024-01-01T10:00:00Z",
            "charges": 5.0
        }
        client.post("/api/v1/simulate/trades", json=buy_trade)
        
        # Partially sell
        sell_trade = {
            "user_id": 123,
            "security_id": 1,
            "side": "SELL",
            "quantity": 50.0,
            "price": 170.0,
            "timestamp": "2024-02-01T10:00:00Z",
            "charges": 3.0
        }
        client.post("/api/v1/simulate/trades", json=sell_trade)
        
        # Get only OPEN lots
        response = client.get("/api/v1/taxlots/?user_id=123&status=OPEN")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 0  # Should be empty since lot is now PARTIAL
        
        # Get PARTIAL lots
        response = client.get("/api/v1/taxlots/?user_id=123&status=PARTIAL")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "PARTIAL"

    def test_invalid_trade_data(self, client):
        """Test API with invalid trade data."""
        invalid_trade = {
            "user_id": 123,
            "security_id": 1,
            "side": "INVALID_SIDE",
            "quantity": -100.0,  # Negative quantity
            "price": -150.0,     # Negative price
            "timestamp": "invalid-date",
            "charges": -5.0      # Negative charges
        }
        
        response = client.post("/api/v1/simulate/trades", json=invalid_trade)
        assert response.status_code == 422  # Validation error

    def test_missing_required_fields(self, client):
        """Test API with missing required fields."""
        incomplete_trade = {
            "user_id": 123,
            "security_id": 1,
            # Missing side, quantity, price
        }
        
        response = client.post("/api/v1/simulate/trades", json=incomplete_trade)
        assert response.status_code == 422  # Validation error

    def test_portfolio_snapshot_nonexistent_user(self, client):
        """Test portfolio snapshot for non-existent user."""
        response = client.get("/api/v1/portfolios/999/snapshot")
        assert response.status_code == 404

    def test_tax_lots_nonexistent_user(self, client):
        """Test tax lots for non-existent user."""
        response = client.get("/api/v1/taxlots/?user_id=999")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 0

    def test_large_quantity_trades(self, client):
        """Test API with large quantity trades."""
        large_trade = {
            "user_id": 123,
            "security_id": 1,
            "side": "BUY",
            "quantity": 999999.9999,
            "price": 150.1234,
            "timestamp": "2024-01-01T10:00:00Z",
            "charges": 5000.5678
        }
        
        response = client.post("/api/v1/simulate/trades", json=large_trade)
        assert response.status_code == 202

    def test_concurrent_trades_same_user(self, client):
        """Test concurrent trades for the same user."""
        trade1 = {
            "user_id": 123,
            "security_id": 1,
            "side": "BUY",
            "quantity": 100.0,
            "price": 150.0,
            "timestamp": "2024-01-01T10:00:00Z",
            "charges": 5.0
        }
        
        trade2 = {
            "user_id": 123,
            "security_id": 1,
            "side": "BUY",
            "quantity": 50.0,
            "price": 160.0,
            "timestamp": "2024-01-01T10:01:00Z",
            "charges": 3.0
        }
        
        # Send both trades
        response1 = client.post("/api/v1/simulate/trades", json=trade1)
        response2 = client.post("/api/v1/simulate/trades", json=trade2)
        
        assert response1.status_code == 202
        assert response2.status_code == 202

    def test_different_users_same_security(self, client):
        """Test trades for different users on same security."""
        trade_user1 = {
            "user_id": 123,
            "security_id": 1,
            "side": "BUY",
            "quantity": 100.0,
            "price": 150.0,
            "timestamp": "2024-01-01T10:00:00Z",
            "charges": 5.0
        }
        
        trade_user2 = {
            "user_id": 456,
            "security_id": 1,
            "side": "BUY",
            "quantity": 200.0,
            "price": 155.0,
            "timestamp": "2024-01-01T10:00:00Z",
            "charges": 8.0
        }
        
        response1 = client.post("/api/v1/simulate/trades", json=trade_user1)
        response2 = client.post("/api/v1/simulate/trades", json=trade_user2)
        
        assert response1.status_code == 202
        assert response2.status_code == 202
        
        # Verify both users have separate portfolios
        portfolio1 = client.get("/api/v1/portfolios/123/snapshot")
        portfolio2 = client.get("/api/v1/portfolios/456/snapshot")
        
        assert portfolio1.status_code == 200
        assert portfolio2.status_code == 200
        
        assert portfolio1.json()["summary"]["user_id"] == 123
        assert portfolio2.json()["summary"]["user_id"] == 456
