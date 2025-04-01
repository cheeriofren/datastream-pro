import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.decomposition import PCA
from typing import Dict, List, Tuple, Optional
import logging
import joblib
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataAnalyzer:
    def __init__(self):
        self.models = {
            'rf': RandomForestRegressor(n_estimators=100, random_state=42),
            'gb': GradientBoostingRegressor(random_state=42),
            'svr': SVR(kernel='rbf')
        }
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95)
        self.best_model = None
        self.model_path = "models"
        os.makedirs(self.model_path, exist_ok=True)
    
    async def prepare_data(self, data: pd.DataFrame, target_col: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Mempersiapkan data untuk analisis dengan feature engineering
        """
        try:
            # Menghapus kolom target
            X = data.drop(columns=[target_col])
            
            # Menambahkan fitur interaksi
            for i in range(len(X.columns)):
                for j in range(i+1, len(X.columns)):
                    X[f'interaction_{i}_{j}'] = X.iloc[:, i] * X.iloc[:, j]
            
            # Menambahkan fitur polinomial
            for col in X.columns:
                X[f'{col}_squared'] = X[col] ** 2
            
            # Menambahkan fitur statistik
            X['mean'] = X.mean(axis=1)
            X['std'] = X.std(axis=1)
            
            y = data[target_col]
            
            return X, y
        except Exception as e:
            logger.error(f"Error saat mempersiapkan data: {str(e)}")
            raise
    
    async def train_model(self, X: np.ndarray, y: np.ndarray, model_type: str = 'rf') -> Dict:
        """
        Melatih model machine learning dengan cross-validation
        """
        try:
            if model_type not in self.models:
                raise ValueError(f"Model type tidak valid: {model_type}")
            
            model = self.models[model_type]
            
            # Cross-validation
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
            
            # Training final model
            model.fit(X, y)
            self.best_model = model
            
            # Menyimpan model
            joblib.dump(model, os.path.join(self.model_path, f'{model_type}_model.joblib'))
            
            # Evaluasi model
            y_pred = model.predict(X)
            mse = mean_squared_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            return {
                "cv_mean": cv_scores.mean(),
                "cv_std": cv_scores.std(),
                "mse": mse,
                "r2": r2,
                "feature_importance": dict(zip(X.columns, model.feature_importances_)) if hasattr(model, 'feature_importances_') else None
            }
        except Exception as e:
            logger.error(f"Error saat melatih model: {str(e)}")
            raise
    
    async def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Melakukan prediksi menggunakan model yang telah dilatih
        """
        try:
            if self.best_model is None:
                raise ValueError("Model belum dilatih")
            
            predictions = self.best_model.predict(X)
            return predictions
        except Exception as e:
            logger.error(f"Error saat melakukan prediksi: {str(e)}")
            raise
    
    async def analyze_trends(self, data: pd.DataFrame) -> Dict:
        """
        Menganalisis tren dalam data dengan analisis statistik lanjutan
        """
        try:
            # Analisis statistik dasar
            basic_stats = {
                "mean": data.mean().to_dict(),
                "std": data.std().to_dict(),
                "skew": data.skew().to_dict(),
                "kurtosis": data.kurtosis().to_dict()
            }
            
            # Analisis korelasi
            correlation = data.corr().to_dict()
            
            # Analisis outlier menggunakan IQR
            outliers = {}
            for column in data.columns:
                Q1 = data[column].quantile(0.25)
                Q3 = data[column].quantile(0.75)
                IQR = Q3 - Q1
                outliers[column] = len(data[(data[column] < (Q1 - 1.5 * IQR)) | (data[column] > (Q3 + 1.5 * IQR))])
            
            # Analisis tren temporal
            temporal_trends = {}
            for column in data.columns:
                if pd.api.types.is_numeric_dtype(data[column]):
                    slope = np.polyfit(range(len(data)), data[column], 1)[0]
                    temporal_trends[column] = {
                        "slope": slope,
                        "direction": "increasing" if slope > 0 else "decreasing"
                    }
            
            return {
                "basic_stats": basic_stats,
                "correlation": correlation,
                "outliers": outliers,
                "temporal_trends": temporal_trends
            }
        except Exception as e:
            logger.error(f"Error saat menganalisis tren: {str(e)}")
            raise
    
    async def detect_anomalies(self, data: pd.DataFrame) -> Dict:
        """
        Mendeteksi anomali dalam data menggunakan berbagai metode
        """
        try:
            anomalies = {}
            
            # Metode 1: Z-score
            for column in data.columns:
                if pd.api.types.is_numeric_dtype(data[column]):
                    z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
                    anomalies[column] = {
                        "z_score": len(data[z_scores > 3]),
                        "threshold": 3
                    }
            
            # Metode 2: Isolation Forest
            from sklearn.ensemble import IsolationForest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            iso_forest.fit(data)
            anomalies["isolation_forest"] = {
                "anomalies": len(data[iso_forest.predict(data) == -1]),
                "percentage": (len(data[iso_forest.predict(data) == -1]) / len(data)) * 100
            }
            
            return anomalies
        except Exception as e:
            logger.error(f"Error saat mendeteksi anomali: {str(e)}")
            raise 