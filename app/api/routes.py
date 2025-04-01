from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
import pandas as pd
from ..services.data_collector import DataCollector
from ..services.data_analyzer import DataAnalyzer
from ..services.data_visualizer import DataVisualizer

router = APIRouter()
data_collector = DataCollector()
data_analyzer = DataAnalyzer()
data_visualizer = DataVisualizer()

@router.get("/data/{source}")
async def get_climate_data(source: str, params: Optional[Dict] = None):
    """
    Mengambil data iklim dari sumber yang ditentukan
    """
    try:
        data = await data_collector.fetch_climate_data(source, params)
        return {"status": "success", "data": data.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_data(data: Dict):
    """
    Menganalisis data iklim
    """
    try:
        df = pd.DataFrame(data)
        trends = await data_analyzer.analyze_trends(df)
        return {"status": "success", "trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/visualize/time-series")
async def create_time_series_visualization(data: Dict, x_col: str, y_col: str):
    """
    Membuat visualisasi time series
    """
    try:
        df = pd.DataFrame(data)
        plot = await data_visualizer.create_time_series_plot(df, x_col, y_col)
        return {"status": "success", "plot": plot}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/visualize/correlation")
async def create_correlation_visualization(data: Dict):
    """
    Membuat visualisasi korelasi
    """
    try:
        df = pd.DataFrame(data)
        plot = await data_visualizer.create_correlation_heatmap(df)
        return {"status": "success", "plot": plot}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 