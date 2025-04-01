import pytest
from datetime import datetime, timedelta
from fastapi import Request
from app.core.rate_limiter import RateLimiter, RateLimitMiddleware, APIKeyRateLimiter
from app.core.database import get_db, init_db
from app.models.api_key import APIKey
from app.models.user import User

@pytest.fixture
def test_db():
    # Inisialisasi database test
    init_db()
    db = next(get_db())
    yield db
    # Cleanup setelah test
    db.query(APIKey).delete()
    db.query(User).delete()
    db.commit()

@pytest.fixture
def test_user(test_db):
    # Buat user test
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    test_db.add(user)
    test_db.commit()
    return user

@pytest.fixture
def test_api_key(test_db, test_user):
    # Buat API key test
    api_key = APIKey(
        key="test_api_key",
        user_id=test_user.id,
        is_active=True
    )
    test_db.add(api_key)
    test_db.commit()
    return api_key

@pytest.fixture
def mock_request():
    # Buat mock request
    class MockRequest:
        def __init__(self, client_host="127.0.0.1", headers=None):
            self.client_host = client_host
            self.headers = headers or {}
    
    return MockRequest()

def test_rate_limiter_creation():
    """Test pembuatan rate limiter"""
    limiter = RateLimiter(requests_per_minute=60)
    assert limiter.requests_per_minute == 60
    assert isinstance(limiter.requests, dict)

def test_rate_limiter_check_limit():
    """Test pengecekan rate limit"""
    limiter = RateLimiter(requests_per_minute=2)
    
    # Buat key
    key = "test_key"
    
    # Cek limit belum terlampaui
    assert limiter.check_rate_limit(key)
    
    # Buat request sampai limit
    assert limiter.check_rate_limit(key)
    
    # Cek limit sudah terlampaui
    assert not limiter.check_rate_limit(key)

def test_rate_limiter_cleanup():
    """Test pembersihan request yang sudah expired"""
    limiter = RateLimiter(requests_per_minute=60)
    
    # Tambahkan request yang sudah expired
    key = "test_key"
    limiter.requests[key] = [
        datetime.utcnow() - timedelta(minutes=2)
    ]
    
    # Cek cleanup
    limiter._cleanup_old_requests()
    assert key not in limiter.requests

def test_rate_limit_middleware(mock_request):
    """Test rate limit middleware"""
    middleware = RateLimitMiddleware(requests_per_minute=2)
    
    # Cek endpoint yang di-skip
    mock_request.url = "/docs"
    assert middleware.should_skip_rate_limit(mock_request)
    
    # Cek endpoint normal
    mock_request.url = "/api/data"
    assert not middleware.should_skip_rate_limit(mock_request)

def test_api_key_rate_limiter(test_db, test_api_key):
    """Test rate limiter untuk API key"""
    limiter = APIKeyRateLimiter(requests_per_minute=2)
    
    # Cek limit belum terlampaui
    assert limiter.check_rate_limit(test_api_key.key)
    
    # Buat request sampai limit
    assert limiter.check_rate_limit(test_api_key.key)
    
    # Cek limit sudah terlampaui
    assert not limiter.check_rate_limit(test_api_key.key)

def test_get_remaining_requests():
    """Test mendapatkan sisa request yang diizinkan"""
    limiter = RateLimiter(requests_per_minute=2)
    key = "test_key"
    
    # Cek sisa request awal
    assert limiter.get_remaining_requests(key) == 2
    
    # Buat request
    limiter.check_rate_limit(key)
    
    # Cek sisa request setelah request
    assert limiter.get_remaining_requests(key) == 1

def test_rate_limiter_with_different_keys():
    """Test rate limiter dengan key yang berbeda"""
    limiter = RateLimiter(requests_per_minute=2)
    
    # Cek limit untuk key pertama
    assert limiter.check_rate_limit("key1")
    assert limiter.check_rate_limit("key1")
    assert not limiter.check_rate_limit("key1")
    
    # Cek limit untuk key kedua
    assert limiter.check_rate_limit("key2")
    assert limiter.check_rate_limit("key2")
    assert not limiter.check_rate_limit("key2")

def test_rate_limiter_reset():
    """Test reset rate limiter"""
    limiter = RateLimiter(requests_per_minute=2)
    key = "test_key"
    
    # Buat request sampai limit
    assert limiter.check_rate_limit(key)
    assert limiter.check_rate_limit(key)
    assert not limiter.check_rate_limit(key)
    
    # Reset rate limiter
    limiter.reset()
    
    # Cek bisa request lagi
    assert limiter.check_rate_limit(key)
    assert limiter.check_rate_limit(key)
    assert not limiter.check_rate_limit(key)

def test_rate_limiter_with_custom_window():
    """Test rate limiter dengan window time yang berbeda"""
    limiter = RateLimiter(requests_per_minute=2, window_seconds=30)
    key = "test_key"
    
    # Buat request sampai limit
    assert limiter.check_rate_limit(key)
    assert limiter.check_rate_limit(key)
    assert not limiter.check_rate_limit(key)
    
    # Tunggu window time
    import time
    time.sleep(31)
    
    # Cek bisa request lagi
    assert limiter.check_rate_limit(key)
    assert limiter.check_rate_limit(key)
    assert not limiter.check_rate_limit(key) 