import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.services.data_collector import DataCollector
from app.core.logging_config import get_logger

logger = get_logger(__name__)

@pytest.fixture
def data_collector():
    return DataCollector()

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', periods=10, freq='D'),
        'temperature': np.random.normal(25, 5, 10),
        'humidity': np.random.normal(60, 10, 10),
        'pressure': np.random.normal(1013, 10, 10)
    })

@pytest.mark.asyncio
async def test_fetch_climate_data(data_collector):
    """Test pengambilan data iklim"""
    data = await data_collector.fetch_climate_data("climate_data_ca")
    assert isinstance(data, pd.DataFrame)

@pytest.mark.asyncio
async def test_process_raw_data(data_collector, sample_data):
    """Test pemrosesan data mentah"""
    processed_data = await data_collector.process_raw_data(sample_data)
    
    # Cek tipe data
    assert isinstance(processed_data, pd.DataFrame)
    
    # Cek tidak ada missing values
    assert not processed_data.isnull().any().any()
    
    # Cek normalisasi
    numeric_cols = processed_data.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        assert abs(processed_data[col].mean()) < 1e-10
        assert abs(processed_data[col].std() - 1) < 1e-10

@pytest.mark.asyncio
async def test_validate_data(data_collector, sample_data):
    """Test validasi data"""
    validation_results = await data_collector.validate_data(sample_data)
    
    # Cek tipe hasil
    assert isinstance(validation_results, dict)
    
    # Cek hasil validasi
    assert validation_results["has_data"]
    assert validation_results["no_missing_values"]
    assert validation_results["no_duplicates"]

@pytest.mark.asyncio
async def test_fetch_historical_data(data_collector):
    """Test pengambilan data historis"""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 10)
    
    data = await data_collector.fetch_historical_data(
        "climate_data_ca",
        start_date,
        end_date
    )
    
    assert isinstance(data, pd.DataFrame)
    if not data.empty:
        assert len(data) > 0
        assert "date" in data.columns

@pytest.mark.asyncio
async def test_fetch_multiple_sources(data_collector):
    """Test pengambilan data dari multiple sources"""
    sources = ["climate_data_ca", "globe"]
    results = await data_collector.fetch_multiple_sources(sources)
    
    assert isinstance(results, dict)
    assert all(isinstance(data, pd.DataFrame) for data in results.values())
    assert all(source in results for source in sources)

@pytest.mark.asyncio
async def test_cache_functionality(data_collector):
    """Test fungsionalitas caching"""
    # Ambil data pertama kali
    data1 = await data_collector.fetch_climate_data("climate_data_ca")
    
    # Ambil data kedua kali (seharusnya dari cache)
    data2 = await data_collector.fetch_climate_data("climate_data_ca")
    
    # Cek bahwa kedua data sama
    pd.testing.assert_frame_equal(data1, data2)

@pytest.mark.asyncio
async def test_error_handling(data_collector):
    """Test penanganan error"""
    with pytest.raises(ValueError):
        await data_collector.fetch_climate_data("invalid_source")

@pytest.mark.asyncio
async def test_data_cleaning(data_collector, sample_data):
    """Test pembersihan data"""
    # Tambahkan beberapa outlier
    sample_data.loc[0, 'temperature'] = 1000
    sample_data.loc[1, 'humidity'] = -50
    
    processed_data = await data_collector.process_raw_data(sample_data)
    
    # Cek outlier sudah dihapus
    assert processed_data['temperature'].max() < 1000
    assert processed_data['humidity'].min() > -50

@pytest.mark.asyncio
async def test_data_normalization(data_collector, sample_data):
    """Test normalisasi data"""
    processed_data = await data_collector.process_raw_data(sample_data)
    
    numeric_cols = processed_data.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        # Cek mean mendekati 0
        assert abs(processed_data[col].mean()) < 1e-10
        # Cek std mendekati 1
        assert abs(processed_data[col].std() - 1) < 1e-10 