import pytest
from datetime import datetime
from app.core.database import (
    get_db,
    init_db,
    get_dataset,
    get_user,
    create_dataset,
    add_data_point,
    create_analysis
)
from app.models.user import User
from app.models.dataset import Dataset
from app.models.analysis import Analysis
from app.models.data_point import DataPoint

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

def test_get_db():
    """Test mendapatkan database session"""
    db = next(get_db())
    assert db is not None

def test_init_db():
    """Test inisialisasi database"""
    init_db()
    db = next(get_db())
    # Cek tabel sudah dibuat
    assert "users" in db.execute("SELECT name FROM sqlite_master").fetchall()
    assert "datasets" in db.execute("SELECT name FROM sqlite_master").fetchall()
    assert "analyses" in db.execute("SELECT name FROM sqlite_master").fetchall()
    assert "data_points" in db.execute("SELECT name FROM sqlite_master").fetchall()

def test_get_dataset(test_db, test_user):
    """Test mendapatkan dataset"""
    # Buat dataset
    dataset = Dataset(
        name="Test Dataset",
        source="test_source",
        created_by=test_user.id
    )
    test_db.add(dataset)
    test_db.commit()
    
    # Cek get dataset
    retrieved_dataset = get_dataset(dataset.id)
    assert retrieved_dataset is not None
    assert retrieved_dataset.name == "Test Dataset"

def test_get_user(test_db, test_user):
    """Test mendapatkan user"""
    # Cek get user
    retrieved_user = get_user(test_user.username)
    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"

def test_create_dataset(test_db, test_user):
    """Test pembuatan dataset"""
    dataset_data = {
        "name": "New Dataset",
        "source": "new_source",
        "description": "Test Description",
        "created_by": test_user.id
    }
    
    # Buat dataset
    dataset = create_dataset(**dataset_data)
    
    # Cek dataset tersimpan
    assert dataset.id is not None
    assert dataset.name == dataset_data["name"]
    assert dataset.source == dataset_data["source"]

def test_add_data_point(test_db, test_user):
    """Test penambahan data point"""
    # Buat dataset
    dataset = Dataset(
        name="Test Dataset",
        source="test_source",
        created_by=test_user.id
    )
    test_db.add(dataset)
    test_db.commit()
    
    # Tambah data point
    data_point = add_data_point(
        dataset_id=dataset.id,
        timestamp=datetime.now(),
        value=42.5,
        metadata={"quality": "good"}
    )
    
    # Cek data point tersimpan
    assert data_point.id is not None
    assert data_point.value == 42.5
    assert data_point.metadata == {"quality": "good"}

def test_create_analysis(test_db, test_user):
    """Test pembuatan analysis"""
    # Buat dataset
    dataset = Dataset(
        name="Test Dataset",
        source="test_source",
        created_by=test_user.id
    )
    test_db.add(dataset)
    test_db.commit()
    
    # Buat analysis
    analysis = create_analysis(
        dataset_id=dataset.id,
        analysis_type="time_series",
        parameters={"target_column": "value"},
        created_by=test_user.id
    )
    
    # Cek analysis tersimpan
    assert analysis.id is not None
    assert analysis.analysis_type == "time_series"
    assert analysis.parameters == {"target_column": "value"}

def test_database_relationships(test_db, test_user):
    """Test relasi antar tabel"""
    # Buat dataset
    dataset = Dataset(
        name="Test Dataset",
        source="test_source",
        created_by=test_user.id
    )
    test_db.add(dataset)
    test_db.commit()
    
    # Tambah data points
    for i in range(3):
        add_data_point(
            dataset_id=dataset.id,
            timestamp=datetime.now(),
            value=i
        )
    
    # Buat analysis
    analysis = create_analysis(
        dataset_id=dataset.id,
        analysis_type="time_series",
        created_by=test_user.id
    )
    
    # Cek relasi
    assert len(dataset.data_points) == 3
    assert len(dataset.analyses) == 1
    assert dataset.created_by_user.username == "testuser"

def test_database_constraints(test_db, test_user):
    """Test constraint database"""
    # Test unique constraint pada username
    with pytest.raises(Exception):
        User(
            username="testuser",  # Username sudah ada
            email="another@example.com",
            hashed_password="hashed_password"
        )
    
    # Test foreign key constraint
    with pytest.raises(Exception):
        add_data_point(
            dataset_id=999,  # Dataset ID tidak ada
            timestamp=datetime.now(),
            value=42.5
        )

def test_database_transactions(test_db, test_user):
    """Test transaksi database"""
    # Buat dataset
    dataset = Dataset(
        name="Test Dataset",
        source="test_source",
        created_by=test_user.id
    )
    test_db.add(dataset)
    test_db.commit()
    
    try:
        # Mulai transaksi
        add_data_point(
            dataset_id=dataset.id,
            timestamp=datetime.now(),
            value=42.5
        )
        raise Exception("Simulasi error")
    except Exception:
        # Rollback transaksi
        test_db.rollback()
    
    # Cek data point tidak tersimpan
    data_points = test_db.query(DataPoint).filter_by(dataset_id=dataset.id).all()
    assert len(data_points) == 0 