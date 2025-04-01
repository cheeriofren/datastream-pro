from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi database
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./datastream_pro.db"
)

# Buat engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Buat session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Buat base class
Base = declarative_base()

# Model database
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    api_keys = relationship("APIKey", back_populates="user")

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    is_active = Column(Boolean, default=True)
    user = relationship("User", back_populates="api_keys")

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    source = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(String)  # JSON string
    data_points = relationship("DataPoint", back_populates="dataset")

class DataPoint(Base):
    __tablename__ = "data_points"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    timestamp = Column(DateTime)
    value = Column(Float)
    metadata = Column(String)  # JSON string
    dataset = relationship("Dataset", back_populates="data_points")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    type = Column(String)  # e.g., "trend", "correlation", "prediction"
    parameters = Column(String)  # JSON string
    results = Column(String)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Buat tabel
def init_db():
    Base.metadata.create_all(bind=engine)

# Fungsi utilitas
def get_dataset_by_id(db, dataset_id: int):
    return db.query(Dataset).filter(Dataset.id == dataset_id).first()

def get_user_by_username(db, username: str):
    return db.query(User).filter(User.username == username).first()

def get_active_api_key(db, api_key: str):
    return db.query(APIKey).filter(
        APIKey.key == api_key,
        APIKey.is_active == True
    ).first()

def create_dataset(db, name: str, source: str, description: str, metadata: dict):
    db_dataset = Dataset(
        name=name,
        source=source,
        description=description,
        metadata=str(metadata)
    )
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

def add_data_points(db, dataset_id: int, data_points: list):
    for point in data_points:
        db_point = DataPoint(
            dataset_id=dataset_id,
            timestamp=point["timestamp"],
            value=point["value"],
            metadata=str(point.get("metadata", {}))
        )
        db.add(db_point)
    db.commit()

def create_analysis(db, dataset_id: int, analysis_type: str, parameters: dict, results: dict, user_id: int):
    db_analysis = Analysis(
        dataset_id=dataset_id,
        type=analysis_type,
        parameters=str(parameters),
        results=str(results),
        created_by=user_id
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis 