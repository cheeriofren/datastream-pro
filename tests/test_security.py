import pytest
from datetime import datetime, timedelta
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    verify_api_key,
    get_current_user,
    check_active_user
)
from app.models.user import User
from app.models.api_key import APIKey
from app.core.database import get_db, init_db

@pytest.fixture
def test_db():
    # Inisialisasi database test
    init_db()
    db = next(get_db())
    yield db
    # Cleanup setelah test
    db.query(User).delete()
    db.query(APIKey).delete()
    db.commit()

@pytest.fixture
def test_user(test_db):
    # Buat user test
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
        is_admin=False
    )
    test_db.add(user)
    test_db.commit()
    return user

def test_password_hashing():
    """Test hashing password"""
    password = "testpassword"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_create_access_token():
    """Test pembuatan access token"""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    assert token is not None
    assert isinstance(token, str)

def test_verify_api_key(test_db, test_user):
    """Test verifikasi API key"""
    # Buat API key
    api_key = APIKey(
        key="test_api_key",
        user_id=test_user.id,
        is_active=True
    )
    test_db.add(api_key)
    test_db.commit()
    
    # Verifikasi API key
    assert verify_api_key("test_api_key")
    assert not verify_api_key("invalid_key")

def test_get_current_user(test_db, test_user):
    """Test mendapatkan current user dari token"""
    # Buat token
    token = create_access_token({"sub": test_user.username})
    
    # Dapatkan user dari token
    current_user = get_current_user(token)
    assert current_user.username == test_user.username

def test_check_active_user(test_db, test_user):
    """Test pengecekan user aktif"""
    # Cek user aktif
    assert check_active_user(test_user)
    
    # Set user tidak aktif
    test_user.is_active = False
    test_db.commit()
    assert not check_active_user(test_user)

def test_token_expiration():
    """Test expired token"""
    # Buat token dengan expired time yang sudah lewat
    data = {"sub": "testuser", "exp": datetime.utcnow() - timedelta(minutes=1)}
    token = create_access_token(data)
    
    # Cek token expired
    with pytest.raises(Exception):
        get_current_user(token)

def test_invalid_token():
    """Test token tidak valid"""
    with pytest.raises(Exception):
        get_current_user("invalid_token")

def test_api_key_expiration(test_db, test_user):
    """Test API key expired"""
    # Buat API key dengan last_used yang sudah lewat
    api_key = APIKey(
        key="test_api_key",
        user_id=test_user.id,
        is_active=True,
        last_used=datetime.utcnow() - timedelta(days=31)
    )
    test_db.add(api_key)
    test_db.commit()
    
    # Cek API key expired
    assert not verify_api_key("test_api_key")

def test_api_key_deactivation(test_db, test_user):
    """Test deaktivasi API key"""
    # Buat API key
    api_key = APIKey(
        key="test_api_key",
        user_id=test_user.id,
        is_active=True
    )
    test_db.add(api_key)
    test_db.commit()
    
    # Deaktivasi API key
    api_key.is_active = False
    test_db.commit()
    
    # Cek API key tidak aktif
    assert not verify_api_key("test_api_key")

def test_password_complexity():
    """Test kompleksitas password"""
    # Password terlalu pendek
    with pytest.raises(ValueError):
        get_password_hash("short")
    
    # Password tidak memiliki angka
    with pytest.raises(ValueError):
        get_password_hash("password")
    
    # Password tidak memiliki huruf besar
    with pytest.raises(ValueError):
        get_password_hash("password123")
    
    # Password valid
    password = "Password123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) 