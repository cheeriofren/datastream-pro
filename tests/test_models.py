import pytest
from datetime import datetime
from app.models.user import User
from app.models.dataset import Dataset
from app.models.analysis import Analysis
from app.models.data_point import DataPoint
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
    db.query(Dataset).delete()
    db.query(Analysis).delete()
    db.query(DataPoint).delete()
    db.query(APIKey).delete()
    db.commit()

def test_create_user(test_db):
    """Test pembuatan model User"""
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
    
    # Cek user tersimpan
    saved_user = test_db.query(User).filter_by(username="testuser").first()
    assert saved_user is not None
    assert saved_user.email == "test@example.com"
    assert saved_user.is_active == True

def test_create_dataset(test_db):
    """Test pembuatan model Dataset"""
    # Buat user terlebih dahulu
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    test_db.add(user)
    test_db.commit()
    
    dataset = Dataset(
        name="Test Dataset",
        source="test_source",
        description="Test Description",
        created_by=user.id,
        metadata={"key": "value"}
    )
    test_db.add(dataset)
    test_db.commit()
    
    # Cek dataset tersimpan
    saved_dataset = test_db.query(Dataset).filter_by(name="Test Dataset").first()
    assert saved_dataset is not None
    assert saved_dataset.source == "test_source"
    assert saved_dataset.created_by == user.id
    assert saved_dataset.metadata == {"key": "value"}

def test_create_analysis(test_db):
    """Test pembuatan model Analysis"""
    # Buat user dan dataset terlebih dahulu
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    test_db.add(user)
    test_db.commit()
    
    dataset = Dataset(
        name="Test Dataset",
        source="test_source",
        created_by=user.id
    )
    test_db.add(dataset)
    test_db.commit()
    
    analysis = Analysis(
        dataset_id=dataset.id,
        analysis_type="time_series",
        parameters={"target_column": "value"},
        results={"mse": 0.1, "r2": 0.8},
        created_by=user.id
    )
    test_db.add(analysis)
    test_db.commit()
    
    # Cek analysis tersimpan
    saved_analysis = test_db.query(Analysis).filter_by(dataset_id=dataset.id).first()
    assert saved_analysis is not None
    assert saved_analysis.analysis_type == "time_series"
    assert saved_analysis.parameters == {"target_column": "value"}
    assert saved_analysis.results == {"mse": 0.1, "r2": 0.8}

def test_create_data_point(test_db):
    """Test pembuatan model DataPoint"""
    # Buat dataset terlebih dahulu
    dataset = Dataset(
        name="Test Dataset",
        source="test_source",
        created_by=1
    )
    test_db.add(dataset)
    test_db.commit()
    
    data_point = DataPoint(
        dataset_id=dataset.id,
        timestamp=datetime.now(),
        value=42.5,
        metadata={"quality": "good"}
    )
    test_db.add(data_point)
    test_db.commit()
    
    # Cek data point tersimpan
    saved_data_point = test_db.query(DataPoint).filter_by(dataset_id=dataset.id).first()
    assert saved_data_point is not None
    assert saved_data_point.value == 42.5
    assert saved_data_point.metadata == {"quality": "good"}

def test_create_api_key(test_db):
    """Test pembuatan model APIKey"""
    # Buat user terlebih dahulu
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    test_db.add(user)
    test_db.commit()
    
    api_key = APIKey(
        key="test_api_key",
        user_id=user.id,
        is_active=True
    )
    test_db.add(api_key)
    test_db.commit()
    
    # Cek API key tersimpan
    saved_api_key = test_db.query(APIKey).filter_by(user_id=user.id).first()
    assert saved_api_key is not None
    assert saved_api_key.key == "test_api_key"
    assert saved_api_key.is_active == True

def test_relationships(test_db):
    """Test relasi antar model"""
    # Buat user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    test_db.add(user)
    test_db.commit()
    
    # Buat dataset
    dataset = Dataset(
        name="Test Dataset",
        source="test_source",
        created_by=user.id
    )
    test_db.add(dataset)
    test_db.commit()
    
    # Buat data points
    for i in range(3):
        data_point = DataPoint(
            dataset_id=dataset.id,
            timestamp=datetime.now(),
            value=i
        )
        test_db.add(data_point)
    test_db.commit()
    
    # Buat analysis
    analysis = Analysis(
        dataset_id=dataset.id,
        analysis_type="time_series",
        created_by=user.id
    )
    test_db.add(analysis)
    test_db.commit()
    
    # Cek relasi
    assert len(dataset.data_points) == 3
    assert dataset.analyses[0].analysis_type == "time_series"
    assert dataset.created_by_user.username == "testuser"

def test_cascade_delete(test_db):
    """Test cascade delete"""
    # Buat user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    test_db.add(user)
    test_db.commit()
    
    # Buat dataset
    dataset = Dataset(
        name="Test Dataset",
        source="test_source",
        created_by=user.id
    )
    test_db.add(dataset)
    test_db.commit()
    
    # Buat data points
    for i in range(3):
        data_point = DataPoint(
            dataset_id=dataset.id,
            timestamp=datetime.now(),
            value=i
        )
        test_db.add(data_point)
    test_db.commit()
    
    # Hapus dataset
    test_db.delete(dataset)
    test_db.commit()
    
    # Cek data points juga terhapus
    data_points = test_db.query(DataPoint).filter_by(dataset_id=dataset.id).all()
    assert len(data_points) == 0 