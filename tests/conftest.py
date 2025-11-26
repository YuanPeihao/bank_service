"""Pytest configuration and fixtures"""
import pytest
from fastapi.testclient import TestClient
from src.main import create_app
from src.services.database import Database


@pytest.fixture
def test_db():
    """Create a fresh database instance for each test"""
    db = Database()
    return db


@pytest.fixture
def client(test_db):
    """Create a test client with a fresh database"""
    # Replace the global db instance with test_db
    from src.services import database
    original_db = database.db
    database.db = test_db
    
    app = create_app()
    client = TestClient(app)
    
    yield client
    
    # Restore original db
    database.db = original_db


@pytest.fixture
def sample_account_data():
    """Sample account data for testing"""
    return {
        "account_number": "ACC001",
        "initial_balance": 1000.0
    }

