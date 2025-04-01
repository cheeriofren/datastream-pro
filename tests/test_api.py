import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from app.main import app
from app.core.security import create_access_token
from app.core.database import get_db, init_db
from app.models.user import User
from app.models.dataset import Dataset
from app.models.analysis import Analysis

client = TestClient(app)

@pytest.fixture
def test_db():
    # Inisialisasi database test
    init_db()
    db = next(get_db())
    yield db
    # Cleanup setelah test
    db.query(User).delete()
    db.query(Dataset).delete()
    db.query(Analysis).delete()
    db.commit()

@pytest.fixture
def test_user(test_db):
    # Buat user test
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password",
        is_active=True,
        is_admin=False
    )
    test_db.add(user)
    test_db.commit()
    return user

@pytest.fixture
def test_token(test_user):
    # Buat token test
    return create_access_token(data={"sub": test_user.username})

@pytest.fixture
def test_dataset(test_db, test_user):
    # Buat dataset test
    dataset = Dataset(
        name="Test Dataset",
        source="test_source",
        description="Test Description",
        created_by=test_user.id
    )
    test_db.add(dataset)
    test_db.commit()
    return dataset

def test_read_root():
    """Test endpoint root"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_read_health():
    """Test endpoint health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_user(test_db):
    """Test pembuatan user baru"""
    user_data = {
        "username": "newuser",
        "email": "new@example.com",
        "full_name": "New User",
        "password": "password123"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert response.json()["username"] == user_data["username"]

def test_login(test_user):
    """Test login user"""
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_user_me(test_token):
    """Test mendapatkan data user yang sedang login"""
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_create_dataset(test_token, test_user):
    """Test pembuatan dataset baru"""
    dataset_data = {
        "name": "New Dataset",
        "source": "new_source",
        "description": "New Description"
    }
    response = client.post(
        "/datasets/",
        json=dataset_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == dataset_data["name"]

def test_get_datasets(test_token, test_dataset):
    """Test mendapatkan daftar dataset"""
    response = client.get(
        "/datasets/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_dataset(test_token, test_dataset):
    """Test mendapatkan detail dataset"""
    response = client.get(
        f"/datasets/{test_dataset.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == test_dataset.id

def test_create_analysis(test_token, test_dataset):
    """Test pembuatan analisis baru"""
    analysis_data = {
        "dataset_id": test_dataset.id,
        "analysis_type": "time_series",
        "parameters": {
            "target_column": "value",
            "time_column": "timestamp"
        }
    }
    response = client.post(
        "/analyses/",
        json=analysis_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 201
    assert response.json()["analysis_type"] == analysis_data["analysis_type"]

def test_get_analyses(test_token, test_dataset):
    """Test mendapatkan daftar analisis"""
    response = client.get(
        "/analyses/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_analysis(test_token, test_dataset):
    """Test mendapatkan detail analisis"""
    # Buat analisis test
    analysis = Analysis(
        dataset_id=test_dataset.id,
        analysis_type="time_series",
        parameters={"target_column": "value"},
        created_by=test_dataset.created_by
    )
    test_db.add(analysis)
    test_db.commit()
    
    response = client.get(
        f"/analyses/{analysis.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == analysis.id

def test_unauthorized_access():
    """Test akses tanpa token"""
    response = client.get("/users/me")
    assert response.status_code == 401

def test_invalid_token():
    """Test akses dengan token tidak valid"""
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401 