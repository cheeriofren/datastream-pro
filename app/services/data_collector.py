import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
import logging
import aiohttp
import asyncio
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import hashlib
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        self.sources = {
            "climate_data_ca": "https://climatedata.ca/",
            "globe": "https://www.globe.gov/",
            "nasa_earth_data": "https://earthdata.nasa.gov/",
            "noaa_climate": "https://www.climate.gov/"
        }
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_cache_key(self, source: str, params: Dict) -> str:
        """
        Membuat kunci cache unik berdasarkan sumber dan parameter
        """
        param_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(f"{source}:{param_str}".encode()).hexdigest()
    
    async def _check_cache(self, cache_key: str) -> Optional[pd.DataFrame]:
        """
        Memeriksa cache untuk data yang tersimpan
        """
        cache_file = self.cache_dir / f"{cache_key}.parquet"
        if cache_file.exists():
            try:
                return pd.read_parquet(cache_file)
            except Exception as e:
                logger.warning(f"Error membaca cache: {str(e)}")
        return None
    
    async def _save_to_cache(self, cache_key: str, data: pd.DataFrame):
        """
        Menyimpan data ke cache
        """
        cache_file = self.cache_dir / f"{cache_key}.parquet"
        try:
            data.to_parquet(cache_file)
        except Exception as e:
            logger.warning(f"Error menyimpan ke cache: {str(e)}")
    
    async def fetch_climate_data(self, source: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Mengambil data iklim dari sumber yang ditentukan dengan caching dan error handling
        """
        try:
            if source not in self.sources:
                raise ValueError(f"Sumber data tidak valid: {source}")
            
            params = params or {}
            cache_key = self._get_cache_key(source, params)
            
            # Cek cache
            cached_data = await self._check_cache(cache_key)
            if cached_data is not None:
                logger.info(f"Menggunakan data dari cache untuk {source}")
                return cached_data
            
            # Implementasi pengambilan data spesifik untuk setiap sumber
            if source == "climate_data_ca":
                data = await self._fetch_climate_data_ca(params)
            elif source == "globe":
                data = await self._fetch_globe_data(params)
            elif source == "nasa_earth_data":
                data = await self._fetch_nasa_data(params)
            else:  # noaa_climate
                data = await self._fetch_noaa_data(params)
            
            # Simpan ke cache
            await self._save_to_cache(cache_key, data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error saat mengambil data: {str(e)}")
            raise
    
    async def _fetch_climate_data_ca(self, params: Dict) -> pd.DataFrame:
        """
        Mengambil data dari ClimateData.ca
        """
        # Implementasi spesifik untuk ClimateData.ca
        # Ini adalah placeholder - implementasi sebenarnya akan tergantung pada API mereka
        return pd.DataFrame()
    
    async def _fetch_globe_data(self, params: Dict) -> pd.DataFrame:
        """
        Mengambil data dari GLOBE
        """
        # Implementasi spesifik untuk GLOBE
        # Ini adalah placeholder - implementasi sebenarnya akan tergantung pada API mereka
        return pd.DataFrame()
    
    async def _fetch_nasa_data(self, params: Dict) -> pd.DataFrame:
        """
        Mengambil data dari NASA Earth Data
        """
        # Implementasi spesifik untuk NASA Earth Data
        # Ini adalah placeholder - implementasi sebenarnya akan tergantung pada API mereka
        return pd.DataFrame()
    
    async def _fetch_noaa_data(self, params: Dict) -> pd.DataFrame:
        """
        Mengambil data dari NOAA Climate
        """
        # Implementasi spesifik untuk NOAA Climate
        # Ini adalah placeholder - implementasi sebenarnya akan tergantung pada API mereka
        return pd.DataFrame()
    
    async def process_raw_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Memproses data mentah menjadi format yang dapat digunakan
        """
        try:
            # Pembersihan data
            data = data.copy()
            
            # Menghapus duplikat
            data = data.drop_duplicates()
            
            # Menangani missing values
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].mean())
            
            categorical_cols = data.select_dtypes(include=['object']).columns
            data[categorical_cols] = data[categorical_cols].fillna('unknown')
            
            # Menangani outliers menggunakan IQR
            for col in numeric_cols:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                data = data[~((data[col] < (Q1 - 1.5 * IQR)) | (data[col] > (Q3 + 1.5 * IQR)))]
            
            # Normalisasi data numerik
            data[numeric_cols] = (data[numeric_cols] - data[numeric_cols].mean()) / data[numeric_cols].std()
            
            return data
        except Exception as e:
            logger.error(f"Error saat memproses data: {str(e)}")
            raise
    
    async def validate_data(self, data: pd.DataFrame) -> Dict[str, bool]:
        """
        Memvalidasi kualitas data dengan berbagai metrik
        """
        try:
            validation_results = {
                "has_data": len(data) > 0,
                "has_required_columns": True,  # Implementasikan sesuai kebutuhan
                "no_missing_values": not data.isnull().any().any(),
                "no_duplicates": len(data) == len(data.drop_duplicates()),
                "data_types_valid": True,  # Implementasikan sesuai kebutuhan
                "value_ranges_valid": True  # Implementasikan sesuai kebutuhan
            }
            
            # Tambahan validasi untuk data numerik
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                validation_results[f"{col}_has_valid_range"] = (
                    data[col].min() >= -1e6 and data[col].max() <= 1e6
                )
            
            return validation_results
        except Exception as e:
            logger.error(f"Error saat memvalidasi data: {str(e)}")
            return {"error": str(e)}
    
    async def fetch_historical_data(self, source: str, start_date: datetime, 
                                  end_date: datetime, params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Mengambil data historis dalam rentang waktu tertentu
        """
        try:
            all_data = []
            current_date = start_date
            
            while current_date <= end_date:
                params = params or {}
                params['date'] = current_date.strftime('%Y-%m-%d')
                
                data = await self.fetch_climate_data(source, params)
                if not data.empty:
                    all_data.append(data)
                
                current_date += timedelta(days=1)
            
            if all_data:
                return pd.concat(all_data, ignore_index=True)
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error saat mengambil data historis: {str(e)}")
            raise
    
    async def fetch_multiple_sources(self, sources: List[str], 
                                   params: Optional[Dict] = None) -> Dict[str, pd.DataFrame]:
        """
        Mengambil data dari beberapa sumber secara paralel
        """
        try:
            tasks = [self.fetch_climate_data(source, params) for source in sources]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                source: result for source, result in zip(sources, results)
                if not isinstance(result, Exception)
            }
        except Exception as e:
            logger.error(f"Error saat mengambil data dari multiple sources: {str(e)}")
            raise 