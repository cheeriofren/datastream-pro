import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.services.data_visualizer import DataVisualizer
from app.core.logging_config import get_logger

logger = get_logger(__name__)

@pytest.fixture
def data_visualizer():
    return DataVisualizer()

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

@pytest.mark.asyncio
async def test_create_time_series_plot(data_visualizer, sample_data):
    """Test pembuatan plot time series"""
    fig = await data_visualizer.create_time_series_plot(
        sample_data,
        'value',
        'timestamp'
    )
    
    # Cek tipe data
    assert fig is not None
    assert hasattr(fig, 'to_json')
    
    # Cek data
    data = fig.to_dict()
    assert 'data' in data
    assert len(data['data']) > 0

@pytest.mark.asyncio
async def test_create_correlation_heatmap(data_visualizer, sample_data):
    """Test pembuatan correlation heatmap"""
    # Tambahkan beberapa kolom untuk korelasi
    sample_data['value2'] = sample_data['value'] * 0.5 + np.random.normal(0, 1, 100)
    sample_data['value3'] = sample_data['value'] * -0.3 + np.random.normal(0, 1, 100)
    
    fig = await data_visualizer.create_correlation_heatmap(
        sample_data,
        ['value', 'value2', 'value3']
    )
    
    # Cek tipe data
    assert fig is not None
    assert hasattr(fig, 'to_json')
    
    # Cek data
    data = fig.to_dict()
    assert 'data' in data
    assert len(data['data']) > 0

@pytest.mark.asyncio
async def test_create_distribution_plot(data_visualizer, sample_data):
    """Test pembuatan distribution plot"""
    fig = await data_visualizer.create_distribution_plot(
        sample_data,
        'value'
    )
    
    # Cek tipe data
    assert fig is not None
    assert hasattr(fig, 'to_json')
    
    # Cek data
    data = fig.to_dict()
    assert 'data' in data
    assert len(data['data']) > 0

@pytest.mark.asyncio
async def test_create_pca_plot(data_visualizer, sample_data):
    """Test pembuatan PCA plot"""
    # Tambahkan beberapa kolom untuk PCA
    sample_data['value2'] = sample_data['value'] * 0.5 + np.random.normal(0, 1, 100)
    sample_data['value3'] = sample_data['value'] * -0.3 + np.random.normal(0, 1, 100)
    
    fig = await data_visualizer.create_pca_plot(
        sample_data,
        ['value', 'value2', 'value3']
    )
    
    # Cek tipe data
    assert fig is not None
    assert hasattr(fig, 'to_json')
    
    # Cek data
    data = fig.to_dict()
    assert 'data' in data
    assert len(data['data']) > 0

@pytest.mark.asyncio
async def test_create_feature_importance_plot(data_visualizer, sample_data):
    """Test pembuatan feature importance plot"""
    # Tambahkan beberapa kolom untuk feature importance
    sample_data['value2'] = sample_data['value'] * 0.5 + np.random.normal(0, 1, 100)
    sample_data['value3'] = sample_data['value'] * -0.3 + np.random.normal(0, 1, 100)
    
    # Buat feature importance dictionary
    importance = {
        'value': 0.5,
        'value2': 0.3,
        'value3': 0.2
    }
    
    fig = await data_visualizer.create_feature_importance_plot(importance)
    
    # Cek tipe data
    assert fig is not None
    assert hasattr(fig, 'to_json')
    
    # Cek data
    data = fig.to_dict()
    assert 'data' in data
    assert len(data['data']) > 0

@pytest.mark.asyncio
async def test_create_box_plot(data_visualizer, sample_data):
    """Test pembuatan box plot"""
    # Tambahkan kolom kategori
    sample_data['category'] = np.random.choice(['A', 'B', 'C'], 100)
    
    fig = await data_visualizer.create_box_plot(
        sample_data,
        'value',
        'category'
    )
    
    # Cek tipe data
    assert fig is not None
    assert hasattr(fig, 'to_json')
    
    # Cek data
    data = fig.to_dict()
    assert 'data' in data
    assert len(data['data']) > 0

@pytest.mark.asyncio
async def test_create_scatter_plot(data_visualizer, sample_data):
    """Test pembuatan scatter plot"""
    # Tambahkan kolom untuk scatter plot
    sample_data['value2'] = sample_data['value'] * 0.5 + np.random.normal(0, 1, 100)
    
    fig = await data_visualizer.create_scatter_plot(
        sample_data,
        'value',
        'value2'
    )
    
    # Cek tipe data
    assert fig is not None
    assert hasattr(fig, 'to_json')
    
    # Cek data
    data = fig.to_dict()
    assert 'data' in data
    assert len(data['data']) > 0

@pytest.mark.asyncio
async def test_create_histogram(data_visualizer, sample_data):
    """Test pembuatan histogram"""
    fig = await data_visualizer.create_histogram(
        sample_data,
        'value'
    )
    
    # Cek tipe data
    assert fig is not None
    assert hasattr(fig, 'to_json')
    
    # Cek data
    data = fig.to_dict()
    assert 'data' in data
    assert len(data['data']) > 0 