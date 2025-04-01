import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.services.data_processor import DataProcessor
from app.core.logging_config import get_logger

logger = get_logger(__name__)

@pytest.fixture
def data_processor():
    return DataProcessor()

@pytest.fixture
def sample_data():
    # Buat data sample dengan trend dan seasonal pattern
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    trend = np.linspace(0, 10, 100)
    seasonal = 5 * np.sin(np.linspace(0, 4*np.pi, 100))
    noise = np.random.normal(0, 1, 100)
    
    return pd.DataFrame({
        'timestamp': dates,
        'value': trend + seasonal + noise
    })

@pytest.fixture
def sample_data_with_missing():
    # Buat data sample dengan missing values
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    values = np.random.normal(0, 1, 100)
    values[10:20] = np.nan  # Missing values
    values[40:50] = np.nan  # Missing values
    
    return pd.DataFrame({
        'timestamp': dates,
        'value': values
    })

@pytest.fixture
def sample_data_with_outliers():
    # Buat data sample dengan outliers
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    values = np.random.normal(0, 1, 100)
    values[10] = 1000  # Outlier
    values[20] = -1000  # Outlier
    
    return pd.DataFrame({
        'timestamp': dates,
        'value': values
    })

def test_handle_missing_values(data_processor, sample_data_with_missing):
    """Test penanganan missing values"""
    # Handle missing values
    processed_data = data_processor.handle_missing_values(sample_data_with_missing)
    
    # Cek tidak ada missing values
    assert not processed_data.isnull().any().any()
    
    # Cek jumlah baris tetap sama
    assert len(processed_data) == len(sample_data_with_missing)

def test_handle_outliers(data_processor, sample_data_with_outliers):
    """Test penanganan outliers"""
    # Handle outliers
    processed_data = data_processor.handle_outliers(sample_data_with_outliers)
    
    # Cek outliers sudah dihapus
    assert processed_data['value'].max() < 1000
    assert processed_data['value'].min() > -1000
    
    # Cek jumlah baris berkurang
    assert len(processed_data) < len(sample_data_with_outliers)

def test_normalize_data(data_processor, sample_data):
    """Test normalisasi data"""
    # Normalisasi data
    processed_data = data_processor.normalize_data(sample_data)
    
    # Cek mean mendekati 0
    assert abs(processed_data['value'].mean()) < 1e-10
    
    # Cek std mendekati 1
    assert abs(processed_data['value'].std() - 1) < 1e-10

def test_create_features(data_processor, sample_data):
    """Test pembuatan features"""
    # Buat features
    processed_data = data_processor.create_features(sample_data)
    
    # Cek features baru
    assert 'hour' in processed_data.columns
    assert 'day' in processed_data.columns
    assert 'month' in processed_data.columns
    assert 'year' in processed_data.columns
    assert 'dayofweek' in processed_data.columns

def test_create_interaction_features(data_processor, sample_data):
    """Test pembuatan interaction features"""
    # Tambah kolom untuk interaction features
    sample_data['value2'] = sample_data['value'] * 0.5 + np.random.normal(0, 1, 100)
    
    # Buat interaction features
    processed_data = data_processor.create_interaction_features(
        sample_data,
        ['value', 'value2']
    )
    
    # Cek interaction features
    assert 'value_value2' in processed_data.columns

def test_create_polynomial_features(data_processor, sample_data):
    """Test pembuatan polynomial features"""
    # Buat polynomial features
    processed_data = data_processor.create_polynomial_features(
        sample_data,
        ['value'],
        degree=2
    )
    
    # Cek polynomial features
    assert 'value_squared' in processed_data.columns

def test_create_statistical_features(data_processor, sample_data):
    """Test pembuatan statistical features"""
    # Buat statistical features
    processed_data = data_processor.create_statistical_features(
        sample_data,
        ['value'],
        window=7
    )
    
    # Cek statistical features
    assert 'value_rolling_mean' in processed_data.columns
    assert 'value_rolling_std' in processed_data.columns
    assert 'value_rolling_max' in processed_data.columns
    assert 'value_rolling_min' in processed_data.columns

def test_handle_duplicates(data_processor, sample_data):
    """Test penanganan duplicates"""
    # Tambah duplicates
    duplicated_data = pd.concat([sample_data, sample_data])
    
    # Handle duplicates
    processed_data = data_processor.handle_duplicates(duplicated_data)
    
    # Cek tidak ada duplicates
    assert len(processed_data) == len(sample_data)

def test_handle_categorical_features(data_processor):
    """Test penanganan categorical features"""
    # Buat data dengan categorical features
    data = pd.DataFrame({
        'category': ['A', 'B', 'C', 'A', 'B'],
        'value': [1, 2, 3, 4, 5]
    })
    
    # Handle categorical features
    processed_data = data_processor.handle_categorical_features(data)
    
    # Cek categorical features sudah di-encode
    assert 'category_A' in processed_data.columns
    assert 'category_B' in processed_data.columns
    assert 'category_C' in processed_data.columns

def test_handle_temporal_features(data_processor, sample_data):
    """Test penanganan temporal features"""
    # Handle temporal features
    processed_data = data_processor.handle_temporal_features(sample_data)
    
    # Cek temporal features
    assert 'hour' in processed_data.columns
    assert 'day' in processed_data.columns
    assert 'month' in processed_data.columns
    assert 'year' in processed_data.columns
    assert 'dayofweek' in processed_data.columns
    assert 'is_weekend' in processed_data.columns

def test_handle_skewness(data_processor, sample_data):
    """Test penanganan skewness"""
    # Buat data skewed
    skewed_data = sample_data.copy()
    skewed_data['value'] = np.exp(skewed_data['value'])
    
    # Handle skewness
    processed_data = data_processor.handle_skewness(skewed_data)
    
    # Cek skewness berkurang
    original_skew = skewed_data['value'].skew()
    processed_skew = processed_data['value'].skew()
    assert abs(processed_skew) < abs(original_skew)

def test_handle_multicollinearity(data_processor, sample_data):
    """Test penanganan multicollinearity"""
    # Tambah kolom yang berkorelasi
    sample_data['value2'] = sample_data['value'] * 0.9 + np.random.normal(0, 0.1, 100)
    sample_data['value3'] = sample_data['value'] * 0.8 + np.random.normal(0, 0.2, 100)
    
    # Handle multicollinearity
    processed_data = data_processor.handle_multicollinearity(
        sample_data,
        ['value', 'value2', 'value3']
    )
    
    # Cek korelasi berkurang
    correlation_matrix = processed_data[['value', 'value2', 'value3']].corr()
    assert abs(correlation_matrix.iloc[0, 1]) < 0.9
    assert abs(correlation_matrix.iloc[0, 2]) < 0.8 