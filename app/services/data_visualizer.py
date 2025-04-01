import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
import io
import base64
from scipy import stats
from sklearn.decomposition import PCA
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataVisualizer:
    def __init__(self):
        plt.style.use('seaborn')
        self.color_palette = sns.color_palette("husl", 10)
    
    async def create_time_series_plot(self, data: pd.DataFrame, x_col: str, y_col: str, 
                                    title: Optional[str] = None) -> str:
        """
        Membuat plot time series interaktif dengan trend line dan confidence interval
        """
        try:
            fig = go.Figure()
            
            # Plot data utama
            fig.add_trace(go.Scatter(
                x=data[x_col],
                y=data[y_col],
                mode='lines+markers',
                name='Data',
                line=dict(color=self.color_palette[0])
            ))
            
            # Menambahkan trend line
            z = np.polyfit(range(len(data)), data[y_col], 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=data[x_col],
                y=p(range(len(data))),
                mode='lines',
                name='Trend Line',
                line=dict(color=self.color_palette[1], dash='dash')
            ))
            
            # Menambahkan confidence interval
            confidence = 0.95
            std_err = stats.sem(data[y_col])
            ci = std_err * stats.t.ppf((1 + confidence) / 2, len(data) - 1)
            
            fig.add_trace(go.Scatter(
                x=data[x_col],
                y=data[y_col] + ci,
                mode='lines',
                name='Upper CI',
                line=dict(width=0, color=self.color_palette[2])
            ))
            
            fig.add_trace(go.Scatter(
                x=data[x_col],
                y=data[y_col] - ci,
                mode='lines',
                name='Lower CI',
                line=dict(width=0, color=self.color_palette[2]),
                fill='tonexty'
            ))
            
            # Update layout
            fig.update_layout(
                title=title or f'Time Series Plot: {y_col}',
                xaxis_title=x_col,
                yaxis_title=y_col,
                hovermode='x unified',
                showlegend=True
            )
            
            return fig.to_json()
        except Exception as e:
            logger.error(f"Error saat membuat time series plot: {str(e)}")
            raise
    
    async def create_correlation_heatmap(self, data: pd.DataFrame, 
                                       title: Optional[str] = None) -> str:
        """
        Membuat heatmap korelasi interaktif dengan dendrogram
        """
        try:
            corr_matrix = data.corr()
            
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=np.round(corr_matrix, 2),
                texttemplate='%{text}',
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title=title or 'Correlation Heatmap',
                xaxis_title='Features',
                yaxis_title='Features',
                height=800,
                width=800
            )
            
            return fig.to_json()
        except Exception as e:
            logger.error(f"Error saat membuat correlation heatmap: {str(e)}")
            raise
    
    async def create_distribution_plot(self, data: pd.DataFrame, column: str,
                                     title: Optional[str] = None) -> str:
        """
        Membuat plot distribusi interaktif dengan fitur tambahan
        """
        try:
            fig = make_subplots(rows=2, cols=1, 
                              subplot_titles=('Distribution', 'Box Plot'))
            
            # Histogram dengan KDE
            fig.add_trace(
                go.Histogram(
                    x=data[column],
                    name='Histogram',
                    nbinsx=30,
                    histnorm='probability density'
                ),
                row=1, col=1
            )
            
            # KDE
            kde = stats.gaussian_kde(data[column])
            x_range = np.linspace(data[column].min(), data[column].max(), 100)
            fig.add_trace(
                go.Scatter(
                    x=x_range,
                    y=kde(x_range),
                    name='KDE',
                    line=dict(color=self.color_palette[1])
                ),
                row=1, col=1
            )
            
            # Box plot
            fig.add_trace(
                go.Box(
                    y=data[column],
                    name='Box Plot',
                    boxpoints='outliers'
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title=title or f'Distribution Analysis of {column}',
                height=800,
                showlegend=True
            )
            
            return fig.to_json()
        except Exception as e:
            logger.error(f"Error saat membuat distribution plot: {str(e)}")
            raise
    
    async def create_pca_plot(self, data: pd.DataFrame, n_components: int = 2) -> str:
        """
        Membuat visualisasi PCA untuk dimensionality reduction
        """
        try:
            pca = PCA(n_components=n_components)
            pca_result = pca.fit_transform(data)
            
            if n_components == 2:
                fig = px.scatter(
                    x=pca_result[:, 0],
                    y=pca_result[:, 1],
                    title=f'PCA Visualization (Explained Variance: {pca.explained_variance_ratio_.sum():.2%})',
                    labels={'x': f'PC1 ({pca.explained_variance_ratio_[0]:.1%})',
                           'y': f'PC2 ({pca.explained_variance_ratio_[1]:.1%})'}
                )
            else:
                fig = px.scatter_3d(
                    x=pca_result[:, 0],
                    y=pca_result[:, 1],
                    z=pca_result[:, 2],
                    title=f'PCA 3D Visualization (Explained Variance: {pca.explained_variance_ratio_.sum():.2%})',
                    labels={'x': f'PC1 ({pca.explained_variance_ratio_[0]:.1%})',
                           'y': f'PC2 ({pca.explained_variance_ratio_[1]:.1%})',
                           'z': f'PC3 ({pca.explained_variance_ratio_[2]:.1%})'}
                )
            
            return fig.to_json()
        except Exception as e:
            logger.error(f"Error saat membuat PCA plot: {str(e)}")
            raise
    
    async def create_feature_importance_plot(self, feature_importance: Dict[str, float],
                                           title: Optional[str] = None) -> str:
        """
        Membuat plot feature importance interaktif
        """
        try:
            features = list(feature_importance.keys())
            importance = list(feature_importance.values())
            
            fig = go.Figure(go.Bar(
                x=importance,
                y=features,
                orientation='h',
                marker_color=self.color_palette[0]
            ))
            
            fig.update_layout(
                title=title or 'Feature Importance',
                xaxis_title='Importance',
                yaxis_title='Features',
                height=max(400, len(features) * 25)
            )
            
            return fig.to_json()
        except Exception as e:
            logger.error(f"Error saat membuat feature importance plot: {str(e)}")
            raise 