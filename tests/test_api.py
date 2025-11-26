"""Tests for API endpoints"""
import pytest
from fastapi import status


class TestAccountEndpoints:
    """Test account API endpoints"""
    
    def test_create_account_endpoint(self, client):
        """Test POST /accounts endpoint"""
        response = client.post(
            "/accounts",
            json={"account_number": "ACC001", "initial_balance": 1000.0}
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["account_number"] == "ACC001"
        assert data["balance"] == 1000.0
        assert "id" in data
        assert "created_at" in data
    
    def test_create_account_duplicate(self, client):
        """Test creating duplicate account number returns 400"""
        client.post("/accounts", json={"account_number": "ACC001", "initial_balance": 1000.0})
        response = client.post(
            "/accounts",
            json={"account_number": "ACC001", "initial_balance": 500.0}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.json().get("detail", {})
    
    def test_get_account_endpoint(self, client):
        """Test GET /accounts/{id} endpoint"""
        create_response = client.post(
            "/accounts",
            json={"account_number": "ACC001", "initial_balance": 1000.0}
        )
        account_id = create_response.json()["id"]
        
        response = client.get(f"/accounts/{account_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == account_id
        assert data["account_number"] == "ACC001"
        assert data["balance"] == 1000.0
    
    def test_get_account_not_found(self, client):
        """Test GET /accounts/{id} with non-existent ID returns 404"""
        response = client.get("/accounts/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "error" in response.json().get("detail", {})
    
    def test_list_accounts_endpoint(self, client):
        """Test GET /accounts endpoint"""
        client.post("/accounts", json={"account_number": "ACC001", "initial_balance": 100.0})
        client.post("/accounts", json={"account_number": "ACC002", "initial_balance": 200.0})
        
        response = client.get("/accounts")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all("id" in account for account in data)
        assert all("account_number" in account for account in data)
        assert all("balance" in account for account in data)


class TestDepositEndpoints:
    """Test deposit API endpoints"""
    
    def test_deposit_endpoint(self, client):
        """Test POST /accounts/{id}/deposit endpoint"""
        create_response = client.post(
            "/accounts",
            json={"account_number": "ACC001", "initial_balance": 1000.0}
        )
        account_id = create_response.json()["id"]
        
        response = client.post(
            f"/accounts/{account_id}/deposit",
            json={"amount": 500.0}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["balance"] == 1500.0
    
    def test_deposit_account_not_found(self, client):
        """Test deposit to non-existent account returns 404"""
        response = client.post(
            "/accounts/999/deposit",
            json={"amount": 500.0}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_deposit_zero_amount(self, client):
        """Test deposit with zero amount returns 422"""
        create_response = client.post(
            "/accounts",
            json={"account_number": "ACC001", "initial_balance": 1000.0}
        )
        account_id = create_response.json()["id"]
        
        response = client.post(
            f"/accounts/{account_id}/deposit",
            json={"amount": 0.0}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestWithdrawEndpoints:
    """Test withdrawal API endpoints"""
    
    def test_withdraw_endpoint(self, client):
        """Test POST /accounts/{id}/withdraw endpoint"""
        create_response = client.post(
            "/accounts",
            json={"account_number": "ACC001", "initial_balance": 1000.0}
        )
        account_id = create_response.json()["id"]
        
        response = client.post(
            f"/accounts/{account_id}/withdraw",
            json={"amount": 300.0}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["balance"] == 700.0
    
    def test_withdraw_insufficient_balance(self, client):
        """Test withdrawal with insufficient balance returns 400"""
        create_response = client.post(
            "/accounts",
            json={"account_number": "ACC001", "initial_balance": 100.0}
        )
        account_id = create_response.json()["id"]
        
        response = client.post(
            f"/accounts/{account_id}/withdraw",
            json={"amount": 500.0}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        detail = response.json().get("detail", {})
        assert "error" in detail
        assert "insufficient" in detail["error"].lower()
    
    def test_withdraw_account_not_found(self, client):
        """Test withdrawal from non-existent account returns 404"""
        response = client.post(
            "/accounts/999/withdraw",
            json={"amount": 100.0}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTransferEndpoints:
    """Test transfer API endpoints"""
    
    def test_transfer_endpoint(self, client):
        """Test POST /accounts/{id}/transfer endpoint"""
        from_response = client.post(
            "/accounts",
            json={"account_number": "ACC001", "initial_balance": 1000.0}
        )
        to_response = client.post(
            "/accounts",
            json={"account_number": "ACC002", "initial_balance": 500.0}
        )
        from_id = from_response.json()["id"]
        to_id = to_response.json()["id"]
        
        response = client.post(
            f"/accounts/{from_id}/transfer",
            json={"to_account_id": to_id, "amount": 300.0}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["from_account"]["balance"] == 700.0
        assert data["to_account"]["balance"] == 800.0
    
    def test_transfer_insufficient_balance(self, client):
        """Test transfer with insufficient balance returns 400"""
        from_response = client.post(
            "/accounts",
            json={"account_number": "ACC001", "initial_balance": 100.0}
        )
        to_response = client.post(
            "/accounts",
            json={"account_number": "ACC002", "initial_balance": 500.0}
        )
        from_id = from_response.json()["id"]
        to_id = to_response.json()["id"]
        
        response = client.post(
            f"/accounts/{from_id}/transfer",
            json={"to_account_id": to_id, "amount": 500.0}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.json().get("detail", {})
    
    def test_transfer_same_account(self, client):
        """Test transfer to same account returns 400"""
        create_response = client.post(
            "/accounts",
            json={"account_number": "ACC001", "initial_balance": 1000.0}
        )
        account_id = create_response.json()["id"]
        
        response = client.post(
            f"/accounts/{account_id}/transfer",
            json={"to_account_id": account_id, "amount": 300.0}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.json().get("detail", {})
    
    def test_transfer_invalid_account(self, client):
        """Test transfer to non-existent account returns 404"""
        create_response = client.post(
            "/accounts",
            json={"account_number": "ACC001", "initial_balance": 1000.0}
        )
        account_id = create_response.json()["id"]
        
        response = client.post(
            f"/accounts/{account_id}/transfer",
            json={"to_account_id": 999, "amount": 300.0}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_endpoint(self, client):
        """Test GET /health endpoint"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}

