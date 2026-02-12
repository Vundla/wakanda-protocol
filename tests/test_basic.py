"""
Basic tests for Wakanda Protocol
"""

import pytest
from fastapi.testclient import TestClient
from wakanda.api.main import app

client = TestClient(app)


def test_health_check():
    """Test the health endpoint"""
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert "system_info" in data


def test_health_ready():
    """Test the readiness endpoint"""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_health_live():
    """Test the liveness endpoint"""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


def test_fintech_overview():
    """Test fintech module overview"""
    response = client.get("/fintech/")
    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "fintech"
    assert "features" in data


def test_minerals_overview():
    """Test minerals module overview"""
    response = client.get("/minerals/")
    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "minerals"
    assert "supported_minerals" in data


def test_ai_overview():
    """Test AI module overview"""
    response = client.get("/ai/")
    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "ai"
    assert "supported_languages" in data


def test_governance_overview():
    """Test governance module overview"""
    response = client.get("/governance/")
    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "governance"
    assert "compliance_standards" in data


def test_infrastructure_overview():
    """Test infrastructure module overview"""
    response = client.get("/infrastructure/")
    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "infrastructure"
    assert "capabilities" in data


def test_authentication_register():
    """Test user registration"""
    user_data = {
        "username": "testuser",
        "email": "test@wakanda.africa",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["is_active"] is True


def test_authentication_login():
    """Test user login"""
    # First register a user
    user_data = {
        "username": "logintest",
        "email": "logintest@wakanda.africa", 
        "password": "testpassword123"
    }
    client.post("/auth/register", json=user_data)
    
    # Then try to login
    login_data = {
        "username": "logintest",
        "password": "testpassword123"
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"