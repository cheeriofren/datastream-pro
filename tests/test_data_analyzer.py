import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.services.data_analyzer import DataAnalyzer
from app.core.logging_config import get_logger

logger = get_logger(__name__)

@pytest.fixture
def data_analyzer():
    return DataAnalyzer()

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
async def test_prepare_data(data_analyzer, sample_data):
    """Test persiapan data"""
    prepared_data = await data_analyzer.prepare_data(sample_data)
    
    # Cek tipe data
    assert isinstance(prepared_data, pd.DataFrame)
    
    # Cek feature engineering
    assert 'hour' in prepared_data.columns
    assert 'day' in prepared_data.columns
    assert 'month' in prepared_data.columns
    assert 'year' in prepared_data.columns
    assert 'dayofweek' in prepared_data.columns

@pytest.mark.asyncio
async def test_train_model(data_analyzer, sample_data):
    """Test training model"""
    # Persiapkan data
    prepared_data = await data_analyzer.prepare_data(sample_data)
    
    # Train model
    model = await data_analyzer.train_model(prepared_data)
    
    # Cek model
    assert model is not None
    assert hasattr(model, 'predict')

@pytest.mark.asyncio
async def test_predict(data_analyzer, sample_data):
    """Test prediksi"""
    # Persiapkan dan train model
    prepared_data = await data_analyzer.prepare_data(sample_data)
    model = await data_analyzer.train_model(prepared_data)
    
    # Buat data untuk prediksi
    future_dates = pd.date_range(
        start=sample_data['timestamp'].max() + timedelta(days=1),
        periods=10,
        freq='D'
    )
    future_data = pd.DataFrame({'timestamp': future_dates})
    
    # Lakukan prediksi
    predictions = await data_analyzer.predict(model, future_data)
    
    # Cek hasil prediksi
    assert isinstance(predictions, pd.DataFrame)
    assert len(predictions) == len(future_data)
    assert 'predicted_value' in predictions.columns

@pytest.mark.asyncio
async def test_detect_anomalies(data_analyzer, sample_data):
    """Test deteksi anomali"""
    # Tambahkan beberapa anomali
    sample_data.loc[10, 'value'] = 1000
    sample_data.loc[20, 'value'] = -1000
    
    # Deteksi anomali
    anomalies = await data_analyzer.detect_anomalies(sample_data)
    
    # Cek hasil
    assert isinstance(anomalies, pd.DataFrame)
    assert len(anomalies) > 0
    assert 'is_anomaly' in anomalies.columns
    assert anomalies['is_anomaly'].sum() > 0

@pytest.mark.asyncio
async def test_feature_importance(data_analyzer, sample_data):
    """Test perhitungan feature importance"""
    # Persiapkan data
    prepared_data = await data_analyzer.prepare_data(sample_data)
    
    # Hitung feature importance
    importance = await data_analyzer.get_feature_importance(prepared_data)
    
    # Cek hasil
    assert isinstance(importance, dict)
    assert len(importance) > 0
    assert all(isinstance(v, float) for v in importance.values())
    assert all(v >= 0 for v in importance.values())

@pytest.mark.asyncio
async def test_model_evaluation(data_analyzer, sample_data):
    """Test evaluasi model"""
    # Persiapkan data
    prepared_data = await data_analyzer.prepare_data(sample_data)
    
    # Train dan evaluasi model
    metrics = await data_analyzer.evaluate_model(prepared_data)
    
    # Cek metrics
    assert isinstance(metrics, dict)
    assert 'mse' in metrics
    assert 'rmse' in metrics
    assert 'r2' in metrics
    assert all(isinstance(v, float) for v in metrics.values())

@pytest.mark.asyncio
async def test_cross_validation(data_analyzer, sample_data):
    """Test cross validation"""
    # Persiapkan data
    prepared_data = await data_analyzer.prepare_data(sample_data)
    
    # Lakukan cross validation
    cv_scores = await data_analyzer.cross_validate(prepared_data)
    
    # Cek hasil
    assert isinstance(cv_scores, dict)
    assert 'mean_score' in cv_scores
    assert 'std_score' in cv_scores
    assert 'scores' in cv_scores
    assert len(cv_scores['scores']) > 0

@pytest.mark.asyncio
async def test_model_selection(data_analyzer, sample_data):
    """Test pemilihan model"""
    # Persiapkan data
    prepared_data = await data_analyzer.prepare_data(sample_data)
    
    # Pilih model terbaik
    best_model = await data_analyzer.select_best_model(prepared_data)
    
    # Cek hasil
    assert best_model is not None
    assert hasattr(best_model, 'predict')
    assert hasattr(best_model, 'score') 