"""
Advanced Analytics Plugin for Building Energy Optimizer.
Provides deep insights and advanced statistical analysis.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
from scipy import stats
from scipy.signal import find_peaks
import warnings

try:
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False

from .base import AnalyticsPlugin

logger = logging.getLogger(__name__)

class AdvancedAnalyticsPlugin(AnalyticsPlugin):
    """Advanced analytics plugin for deep energy insights."""
    
    @property
    def name(self) -> str:
        return "Advanced Energy Analytics"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Advanced statistical analysis and insights for energy data"
    
    @property
    def dependencies(self) -> List[str]:
        return ["scipy", "scikit-learn"]
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize analytics plugin."""
        if not HAS_SKLEARN:
            logger.warning("scikit-learn not available - some features disabled")
        
        self.config = config
        logger.info("Advanced analytics plugin initialized")
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive analytics."""
        energy_data = data.get('energy_data')
        predictions = data.get('predictions')
        building_config = data.get('building_config', {})
        
        if energy_data is None:
            return {'error': 'No energy data provided'}
        
        # Convert to DataFrame if needed
        if isinstance(energy_data, list):
            df = pd.DataFrame(energy_data)
        elif isinstance(energy_data, pd.DataFrame):
            df = energy_data.copy()
        else:
            return {'error': 'Invalid data format'}
        
        # Perform various analyses
        results = {
            'statistical_summary': self._statistical_analysis(df),
            'consumption_patterns': self._pattern_analysis(df),
            'anomaly_detection': self._anomaly_detection(df),
            'efficiency_metrics': self._efficiency_analysis(df, building_config),
            'correlation_analysis': self._correlation_analysis(df),
            'peak_analysis': self._peak_analysis(df),
            'trend_analysis': self._trend_analysis(df),
            'seasonality_analysis': self._seasonality_analysis(df),
            'benchmarking': self._benchmarking_analysis(df, building_config),
            'recommendations': self._generate_advanced_recommendations(df),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Add prediction analysis if available
        if predictions is not None:
            results['prediction_analysis'] = self._prediction_analysis(df, predictions)
        
        return results
    
    def _statistical_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive statistical analysis."""
        if 'energy_consumption' not in df.columns:
            return {'error': 'No energy consumption data'}
        
        consumption = df['energy_consumption']
        
        return {
            'descriptive_stats': {
                'mean': float(consumption.mean()),
                'median': float(consumption.median()),
                'std': float(consumption.std()),
                'min': float(consumption.min()),
                'max': float(consumption.max()),
                'q25': float(consumption.quantile(0.25)),
                'q75': float(consumption.quantile(0.75)),
                'skewness': float(stats.skew(consumption)),
                'kurtosis': float(stats.kurtosis(consumption)),
                'cv': float(consumption.std() / consumption.mean())  # Coefficient of variation
            },
            'distribution_analysis': {
                'normality_test': {
                    'statistic': float(stats.normaltest(consumption)[0]),
                    'p_value': float(stats.normaltest(consumption)[1]),
                    'is_normal': stats.normaltest(consumption)[1] > 0.05
                },
                'outlier_detection': {
                    'iqr_outliers': self._detect_iqr_outliers(consumption),
                    'zscore_outliers': self._detect_zscore_outliers(consumption)
                }
            }
        }
    
    def _pattern_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze consumption patterns."""
        if 'timestamp' not in df.columns or 'energy_consumption' not in df.columns:
            return {'error': 'Missing required columns'}
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        
        return {
            'hourly_patterns': {
                'peak_hours': df.groupby('hour')['energy_consumption'].mean().nlargest(3).index.tolist(),
                'low_hours': df.groupby('hour')['energy_consumption'].mean().nsmallest(3).index.tolist(),
                'hourly_variation': float(df.groupby('hour')['energy_consumption'].mean().std())
            },
            'daily_patterns': {
                'weekday_avg': float(df[df['day_of_week'] < 5]['energy_consumption'].mean()),
                'weekend_avg': float(df[df['day_of_week'] >= 5]['energy_consumption'].mean()),
                'workday_variation': float(df.groupby('day_of_week')['energy_consumption'].mean().std())
            },
            'monthly_patterns': {
                'peak_months': df.groupby('month')['energy_consumption'].mean().nlargest(3).index.tolist(),
                'low_months': df.groupby('month')['energy_consumption'].mean().nsmallest(3).index.tolist(),
                'seasonal_variation': float(df.groupby('month')['energy_consumption'].mean().std())
            }
        }
    
    def _anomaly_detection(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalies in energy consumption."""
        if 'energy_consumption' not in df.columns:
            return {'error': 'No energy consumption data'}
        
        consumption = df['energy_consumption']
        
        # Statistical anomalies
        Q1 = consumption.quantile(0.25)
        Q3 = consumption.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        anomalies = df[(consumption < lower_bound) | (consumption > upper_bound)]
        
        # Time-based anomalies
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df_sorted = df.sort_values('timestamp')
            
            # Sudden spikes (>50% increase from previous reading)
            df_sorted['consumption_change'] = df_sorted['energy_consumption'].pct_change()
            spikes = df_sorted[df_sorted['consumption_change'] > 0.5]
            
            # Prolonged high consumption (>2 hours above 90th percentile)
            high_threshold = consumption.quantile(0.9)
            df_sorted['high_consumption'] = df_sorted['energy_consumption'] > high_threshold
            
            # Find consecutive high consumption periods
            prolonged_high = []
            current_streak = 0
            for idx, is_high in df_sorted['high_consumption'].items():
                if is_high:
                    current_streak += 1
                else:
                    if current_streak >= 2:  # 2+ hours
                        prolonged_high.append({
                            'start_idx': idx - current_streak,
                            'end_idx': idx - 1,
                            'duration_hours': current_streak
                        })
                    current_streak = 0
        else:
            spikes = pd.DataFrame()
            prolonged_high = []
        
        return {
            'statistical_anomalies': {
                'count': len(anomalies),
                'percentage': float(len(anomalies) / len(df) * 100),
                'indices': anomalies.index.tolist()
            },
            'consumption_spikes': {
                'count': len(spikes),
                'max_spike': float(spikes['consumption_change'].max()) if len(spikes) > 0 else 0,
                'spike_indices': spikes.index.tolist()
            },
            'prolonged_high_consumption': {
                'periods_count': len(prolonged_high),
                'periods': prolonged_high
            }
        }
    
    def _efficiency_analysis(self, df: pd.DataFrame, building_config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze building energy efficiency."""
        if 'energy_consumption' not in df.columns:
            return {'error': 'No energy consumption data'}
        
        floor_area = building_config.get('floor_area', 1000)
        building_age = building_config.get('building_age', 10)
        insulation_level = building_config.get('insulation_level', 0.7)
        
        consumption = df['energy_consumption']
        
        # Energy intensity (kWh/m²)
        energy_intensity = consumption.mean() / floor_area * 24 * 365  # Annual kWh/m²
        
        # Benchmarks (typical values)
        benchmarks = {
            'residential': {'excellent': 50, 'good': 100, 'average': 150, 'poor': 200},
            'commercial': {'excellent': 100, 'good': 200, 'average': 300, 'poor': 400},
            'industrial': {'excellent': 200, 'good': 400, 'average': 600, 'poor': 800}
        }
        
        building_type = building_config.get('building_type', 'commercial')
        benchmark = benchmarks.get(building_type, benchmarks['commercial'])
        
        # Determine efficiency rating
        if energy_intensity <= benchmark['excellent']:
            rating = 'Excellent'
            score = 90 + (benchmark['excellent'] - energy_intensity) / benchmark['excellent'] * 10
        elif energy_intensity <= benchmark['good']:
            rating = 'Good'
            score = 70 + (benchmark['good'] - energy_intensity) / (benchmark['good'] - benchmark['excellent']) * 20
        elif energy_intensity <= benchmark['average']:
            rating = 'Average'
            score = 50 + (benchmark['average'] - energy_intensity) / (benchmark['average'] - benchmark['good']) * 20
        elif energy_intensity <= benchmark['poor']:
            rating = 'Poor'
            score = 30 + (benchmark['poor'] - energy_intensity) / (benchmark['poor'] - benchmark['average']) * 20
        else:
            rating = 'Very Poor'
            score = max(0, 30 - (energy_intensity - benchmark['poor']) / benchmark['poor'] * 30)
        
        return {
            'energy_intensity_kwh_m2_year': float(energy_intensity),
            'efficiency_rating': rating,
            'efficiency_score': float(score),
            'benchmark_comparison': {
                'building_type': building_type,
                'vs_excellent': float((energy_intensity - benchmark['excellent']) / benchmark['excellent'] * 100),
                'vs_average': float((energy_intensity - benchmark['average']) / benchmark['average'] * 100)
            },
            'improvement_potential': {
                'to_excellent': max(0, float(energy_intensity - benchmark['excellent'])),
                'to_good': max(0, float(energy_intensity - benchmark['good'])),
                'savings_to_excellent_percent': max(0, float((energy_intensity - benchmark['excellent']) / energy_intensity * 100))
            }
        }
    
    def _correlation_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlations between variables."""
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_columns) < 2:
            return {'error': 'Insufficient numeric columns for correlation analysis'}
        
        correlation_matrix = df[numeric_columns].corr()
        
        # Find strongest correlations with energy consumption
        if 'energy_consumption' in numeric_columns:
            energy_correlations = correlation_matrix['energy_consumption'].drop('energy_consumption')
            strongest_positive = energy_correlations.nlargest(3)
            strongest_negative = energy_correlations.nsmallest(3)
        else:
            strongest_positive = pd.Series(dtype=float)
            strongest_negative = pd.Series(dtype=float)
        
        return {
            'correlation_matrix': correlation_matrix.to_dict(),
            'strongest_positive_correlations': strongest_positive.to_dict(),
            'strongest_negative_correlations': strongest_negative.to_dict(),
            'highly_correlated_pairs': self._find_highly_correlated_pairs(correlation_matrix)
        }
    
    def _find_highly_correlated_pairs(self, corr_matrix: pd.DataFrame) -> List[Dict]:
        """Find highly correlated variable pairs."""
        high_correlations = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                var1 = corr_matrix.columns[i]
                var2 = corr_matrix.columns[j]
                correlation = corr_matrix.iloc[i, j]
                
                if abs(correlation) > 0.7:  # High correlation threshold
                    high_correlations.append({
                        'variable1': var1,
                        'variable2': var2,
                        'correlation': float(correlation),
                        'strength': 'Strong' if abs(correlation) > 0.8 else 'Moderate'
                    })
        
        return sorted(high_correlations, key=lambda x: abs(x['correlation']), reverse=True)
    
    def _peak_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze consumption peaks."""
        if 'energy_consumption' not in df.columns:
            return {'error': 'No energy consumption data'}
        
        consumption = df['energy_consumption'].values
        
        # Find peaks
        peaks, peak_properties = find_peaks(
            consumption, 
            height=np.percentile(consumption, 75),  # Above 75th percentile
            distance=3  # At least 3 hours apart
        )
        
        # Analyze peak characteristics
        peak_analysis = {
            'total_peaks': len(peaks),
            'average_peak_height': float(np.mean(consumption[peaks])) if len(peaks) > 0 else 0,
            'peak_frequency': len(peaks) / len(consumption) * 24,  # Peaks per day
            'peak_indices': peaks.tolist()
        }
        
        # Time-based peak analysis
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            peak_times = df.iloc[peaks]['timestamp']
            
            peak_analysis.update({
                'peak_hours': peak_times.dt.hour.value_counts().head(5).to_dict(),
                'peak_days': peak_times.dt.dayofweek.value_counts().to_dict(),
                'peak_months': peak_times.dt.month.value_counts().to_dict()
            })
        
        return peak_analysis
    
    def _trend_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze consumption trends."""
        if 'energy_consumption' not in df.columns or 'timestamp' not in df.columns:
            return {'error': 'Missing required columns'}
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df_sorted = df.sort_values('timestamp')
        
        # Linear trend
        x = np.arange(len(df_sorted))
        y = df_sorted['energy_consumption'].values
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # Trend classification
        if abs(slope) < 0.01:
            trend_direction = 'Stable'
        elif slope > 0:
            trend_direction = 'Increasing'
        else:
            trend_direction = 'Decreasing'
        
        # Moving averages
        df_sorted['ma_7'] = df_sorted['energy_consumption'].rolling(window=7, min_periods=1).mean()
        df_sorted['ma_24'] = df_sorted['energy_consumption'].rolling(window=24, min_periods=1).mean()
        
        return {
            'linear_trend': {
                'slope': float(slope),
                'intercept': float(intercept),
                'r_squared': float(r_value**2),
                'p_value': float(p_value),
                'direction': trend_direction,
                'significance': 'Significant' if p_value < 0.05 else 'Not significant'
            },
            'moving_averages': {
                'ma_7_current': float(df_sorted['ma_7'].iloc[-1]),
                'ma_24_current': float(df_sorted['ma_24'].iloc[-1]),
                'ma_trend': 'Increasing' if df_sorted['ma_7'].iloc[-1] > df_sorted['ma_24'].iloc[-1] else 'Decreasing'
            }
        }
    
    def _seasonality_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze seasonal patterns."""
        if 'timestamp' not in df.columns or 'energy_consumption' not in df.columns:
            return {'error': 'Missing required columns'}
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['month'] = df['timestamp'].dt.month
        df['season'] = df['month'].apply(self._get_season)
        
        seasonal_stats = df.groupby('season')['energy_consumption'].agg(['mean', 'std']).round(2)
        
        # Seasonal variation coefficient
        seasonal_means = seasonal_stats['mean']
        seasonal_cv = seasonal_means.std() / seasonal_means.mean()
        
        return {
            'seasonal_averages': seasonal_stats.to_dict(),
            'seasonal_variation_coefficient': float(seasonal_cv),
            'peak_season': seasonal_means.idxmax(),
            'low_season': seasonal_means.idxmin(),
            'seasonal_difference_percent': float((seasonal_means.max() - seasonal_means.min()) / seasonal_means.mean() * 100)
        }
    
    def _get_season(self, month: int) -> str:
        """Convert month to season."""
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Fall'
    
    def _benchmarking_analysis(self, df: pd.DataFrame, building_config: Dict[str, Any]) -> Dict[str, Any]:
        """Compare against industry benchmarks."""
        if 'energy_consumption' not in df.columns:
            return {'error': 'No energy consumption data'}
        
        # Industry benchmarks (kWh/m²/year)
        industry_benchmarks = {
            'residential': {
                'excellent': 50, 'good': 80, 'average': 120, 'poor': 160
            },
            'commercial': {
                'office': {'excellent': 100, 'good': 150, 'average': 220, 'poor': 300},
                'retail': {'excellent': 150, 'good': 250, 'average': 350, 'poor': 500},
                'hotel': {'excellent': 200, 'good': 300, 'average': 450, 'poor': 600}
            },
            'industrial': {
                'light': {'excellent': 100, 'good': 200, 'average': 350, 'poor': 500},
                'heavy': {'excellent': 300, 'good': 500, 'average': 800, 'poor': 1200}
            }
        }
        
        building_type = building_config.get('building_type', 'commercial')
        floor_area = building_config.get('floor_area', 1000)
        
        # Calculate annual energy intensity
        avg_hourly = df['energy_consumption'].mean()
        annual_kwh_m2 = (avg_hourly * 24 * 365) / floor_area
        
        # Get appropriate benchmark
        if building_type == 'residential':
            benchmark = industry_benchmarks['residential']
        elif building_type == 'commercial':
            benchmark = industry_benchmarks['commercial']['office']  # Default to office
        else:
            benchmark = industry_benchmarks['industrial']['light']  # Default to light industrial
        
        # Performance rating
        if annual_kwh_m2 <= benchmark['excellent']:
            performance = 'Excellent'
        elif annual_kwh_m2 <= benchmark['good']:
            performance = 'Good'
        elif annual_kwh_m2 <= benchmark['average']:
            performance = 'Average'
        elif annual_kwh_m2 <= benchmark['poor']:
            performance = 'Poor'
        else:
            performance = 'Very Poor'
        
        return {
            'annual_energy_intensity': float(annual_kwh_m2),
            'performance_rating': performance,
            'benchmark_comparison': {
                'vs_excellent': float((annual_kwh_m2 - benchmark['excellent']) / benchmark['excellent'] * 100),
                'vs_average': float((annual_kwh_m2 - benchmark['average']) / benchmark['average'] * 100),
                'improvement_to_excellent': max(0, float(annual_kwh_m2 - benchmark['excellent']))
            },
            'industry_percentile': self._calculate_percentile(annual_kwh_m2, benchmark)
        }
    
    def _calculate_percentile(self, value: float, benchmark: Dict[str, float]) -> float:
        """Calculate percentile within industry benchmark."""
        if value <= benchmark['excellent']:
            return 95.0
        elif value <= benchmark['good']:
            return 75.0
        elif value <= benchmark['average']:
            return 50.0
        elif value <= benchmark['poor']:
            return 25.0
        else:
            return 10.0
    
    def _generate_advanced_recommendations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate advanced optimization recommendations."""
        recommendations = []
        
        if 'energy_consumption' not in df.columns:
            return recommendations
        
        consumption = df['energy_consumption']
        
        # Recommendation 1: Load shifting
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            
            hourly_avg = df.groupby('hour')['energy_consumption'].mean()
            peak_hour = hourly_avg.idxmax()
            off_peak_hour = hourly_avg.idxmin()
            
            if hourly_avg[peak_hour] > hourly_avg[off_peak_hour] * 1.5:
                recommendations.append({
                    'type': 'Load Shifting',
                    'priority': 'High',
                    'description': f'Significant load difference between peak ({peak_hour}:00) and off-peak ({off_peak_hour}:00) hours',
                    'action': f'Shift non-critical loads from {peak_hour}:00 to {off_peak_hour}:00',
                    'potential_savings': '10-15%',
                    'implementation_cost': 'Low',
                    'payback_period': '6-12 months'
                })
        
        # Recommendation 2: Demand response
        peak_consumption = consumption.quantile(0.95)
        avg_consumption = consumption.mean()
        
        if peak_consumption > avg_consumption * 2:
            recommendations.append({
                'type': 'Demand Response',
                'priority': 'Medium',
                'description': 'High peak consumption detected',
                'action': 'Implement demand response system to cap peak loads',
                'potential_savings': '8-12%',
                'implementation_cost': 'Medium',
                'payback_period': '12-18 months'
            })
        
        # Recommendation 3: Efficiency upgrades
        consumption_variability = consumption.std() / consumption.mean()
        
        if consumption_variability > 0.3:
            recommendations.append({
                'type': 'System Optimization',
                'priority': 'Medium',
                'description': 'High consumption variability indicates optimization opportunities',
                'action': 'Upgrade to variable speed drives and smart controls',
                'potential_savings': '15-25%',
                'implementation_cost': 'High',
                'payback_period': '18-36 months'
            })
        
        return recommendations
    
    def _detect_iqr_outliers(self, data: pd.Series) -> Dict[str, Any]:
        """Detect outliers using IQR method."""
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = data[(data < lower_bound) | (data > upper_bound)]
        
        return {
            'count': len(outliers),
            'percentage': float(len(outliers) / len(data) * 100),
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'outlier_indices': outliers.index.tolist()
        }
    
    def _detect_zscore_outliers(self, data: pd.Series, threshold: float = 3.0) -> Dict[str, Any]:
        """Detect outliers using Z-score method."""
        z_scores = np.abs(stats.zscore(data))
        outliers = data[z_scores > threshold]
        
        return {
            'count': len(outliers),
            'percentage': float(len(outliers) / len(data) * 100),
            'threshold': threshold,
            'max_zscore': float(z_scores.max()),
            'outlier_indices': outliers.index.tolist()
        }
    
    def _prediction_analysis(self, df: pd.DataFrame, predictions: np.ndarray) -> Dict[str, Any]:
        """Analyze prediction accuracy and patterns."""
        if 'energy_consumption' not in df.columns:
            return {'error': 'No actual consumption data for comparison'}
        
        actual = df['energy_consumption'].values
        
        # Prediction accuracy metrics
        mae = np.mean(np.abs(actual - predictions))
        mse = np.mean((actual - predictions)**2)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((actual - predictions) / actual)) * 100
        
        # R² score
        r2 = 1 - (np.sum((actual - predictions)**2) / np.sum((actual - np.mean(actual))**2))
        
        # Prediction errors
        errors = actual - predictions
        
        return {
            'accuracy_metrics': {
                'mae': float(mae),
                'mse': float(mse),
                'rmse': float(rmse),
                'mape': float(mape),
                'r2_score': float(r2)
            },
            'error_analysis': {
                'mean_error': float(np.mean(errors)),
                'error_std': float(np.std(errors)),
                'max_absolute_error': float(np.max(np.abs(errors))),
                'error_distribution': {
                    'underestimation_count': int(np.sum(errors > 0)),
                    'overestimation_count': int(np.sum(errors < 0)),
                    'perfect_predictions': int(np.sum(errors == 0))
                }
            },
            'prediction_quality': self._assess_prediction_quality(r2, mape)
        }
    
    def _assess_prediction_quality(self, r2: float, mape: float) -> str:
        """Assess overall prediction quality."""
        if r2 > 0.9 and mape < 5:
            return 'Excellent'
        elif r2 > 0.8 and mape < 10:
            return 'Good'
        elif r2 > 0.7 and mape < 15:
            return 'Fair'
        else:
            return 'Poor'
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute advanced analytics."""
        analysis_type = data.get('analysis_type', 'complete')
        
        if analysis_type == 'complete':
            return self.analyze(data)
        elif analysis_type == 'statistical':
            df = pd.DataFrame(data.get('energy_data', []))
            return self._statistical_analysis(df)
        elif analysis_type == 'patterns':
            df = pd.DataFrame(data.get('energy_data', []))
            return self._pattern_analysis(df)
        elif analysis_type == 'anomalies':
            df = pd.DataFrame(data.get('energy_data', []))
            return self._anomaly_detection(df)
        elif analysis_type == 'efficiency':
            df = pd.DataFrame(data.get('energy_data', []))
            building_config = data.get('building_config', {})
            return self._efficiency_analysis(df, building_config)
        
        return {'error': 'Unknown analysis type'}

class ClusteringPlugin(AnalyticsPlugin):
    """Clustering analysis for energy consumption patterns."""
    
    @property
    def name(self) -> str:
        return "Consumption Clustering"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Cluster similar energy consumption patterns"
    
    @property
    def dependencies(self) -> List[str]:
        return ["scikit-learn"]
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize clustering plugin."""
        if not HAS_SKLEARN:
            logger.error("scikit-learn not available")
            return False
        
        self.n_clusters = config.get('n_clusters', 'auto')
        self.random_state = config.get('random_state', 42)
        
        logger.info("Clustering plugin initialized")
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform clustering analysis."""
        energy_data = data.get('energy_data')
        
        if energy_data is None:
            return {'error': 'No energy data provided'}
        
        df = pd.DataFrame(energy_data)
        
        if 'energy_consumption' not in df.columns:
            return {'error': 'No energy consumption data'}
        
        # Prepare features for clustering
        features = self._prepare_clustering_features(df)
        
        if features is None:
            return {'error': 'Failed to prepare features'}
        
        # Determine optimal number of clusters
        if self.n_clusters == 'auto':
            optimal_k = self._find_optimal_clusters(features)
        else:
            optimal_k = int(self.n_clusters)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=optimal_k, random_state=self.random_state)
        cluster_labels = kmeans.fit_predict(features)
        
        # Analyze clusters
        cluster_analysis = self._analyze_clusters(df, cluster_labels, optimal_k)
        
        return {
            'optimal_clusters': optimal_k,
            'cluster_labels': cluster_labels.tolist(),
            'cluster_analysis': cluster_analysis,
            'cluster_centers': kmeans.cluster_centers_.tolist()
        }
    
    def _prepare_clustering_features(self, df: pd.DataFrame) -> Optional[np.ndarray]:
        """Prepare features for clustering."""
        try:
            # Time-based features
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['hour'] = df['timestamp'].dt.hour
                df['day_of_week'] = df['timestamp'].dt.dayofweek
                df['month'] = df['timestamp'].dt.month
            
            # Select features
            feature_columns = [
                'energy_consumption', 'hour', 'day_of_week', 'month'
            ]
            
            # Add weather features if available
            weather_features = ['temperature', 'humidity', 'solar_radiation']
            for feature in weather_features:
                if feature in df.columns:
                    feature_columns.append(feature)
            
            # Add occupancy if available
            if 'occupancy' in df.columns:
                feature_columns.append('occupancy')
            
            features = df[feature_columns].values
            
            # Scale features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            return features_scaled
            
        except Exception as e:
            logger.error(f"Failed to prepare clustering features: {e}")
            return None
    
    def _find_optimal_clusters(self, features: np.ndarray) -> int:
        """Find optimal number of clusters using elbow method."""
        max_k = min(10, len(features) // 10)  # Reasonable upper bound
        
        if max_k < 2:
            return 2
        
        inertias = []
        
        for k in range(2, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=self.random_state)
            kmeans.fit(features)
            inertias.append(kmeans.inertia_)
        
        # Simple elbow detection
        # Find the point where the rate of decrease significantly drops
        differences = [inertias[i] - inertias[i+1] for i in range(len(inertias)-1)]
        
        if len(differences) > 1:
            # Find the largest drop in the rate of decrease
            rate_changes = [differences[i] - differences[i+1] for i in range(len(differences)-1)]
            optimal_k = rate_changes.index(max(rate_changes)) + 3  # +3 because we start from k=2
        else:
            optimal_k = 3  # Default
        
        return min(optimal_k, max_k)
    
    def _analyze_clusters(self, df: pd.DataFrame, labels: np.ndarray, n_clusters: int) -> Dict[str, Any]:
        """Analyze the characteristics of each cluster."""
        cluster_analysis = {}
        
        for cluster_id in range(n_clusters):
            cluster_mask = labels == cluster_id
            cluster_data = df[cluster_mask]
            
            if len(cluster_data) == 0:
                continue
            
            # Basic statistics
            cluster_stats = {
                'size': len(cluster_data),
                'percentage': float(len(cluster_data) / len(df) * 100),
                'avg_consumption': float(cluster_data['energy_consumption'].mean()),
                'consumption_std': float(cluster_data['energy_consumption'].std())
            }
            
            # Time patterns if available
            if 'timestamp' in df.columns:
                cluster_data['hour'] = pd.to_datetime(cluster_data['timestamp']).dt.hour
                cluster_data['day_of_week'] = pd.to_datetime(cluster_data['timestamp']).dt.dayofweek
                
                cluster_stats['typical_hours'] = cluster_data['hour'].value_counts().head(3).index.tolist()
                cluster_stats['typical_days'] = cluster_data['day_of_week'].value_counts().head(3).index.tolist()
            
            # Characterize cluster
            cluster_stats['characteristics'] = self._characterize_cluster(cluster_data)
            
            cluster_analysis[f'cluster_{cluster_id}'] = cluster_stats
        
        return cluster_analysis
    
    def _characterize_cluster(self, cluster_data: pd.DataFrame) -> str:
        """Characterize a cluster based on its patterns."""
        avg_consumption = cluster_data['energy_consumption'].mean()
        overall_avg = cluster_data['energy_consumption'].mean()  # This should be passed from parent
        
        if avg_consumption > overall_avg * 1.3:
            base_char = "High consumption"
        elif avg_consumption < overall_avg * 0.7:
            base_char = "Low consumption"
        else:
            base_char = "Medium consumption"
        
        # Add time characteristics if available
        if 'hour' in cluster_data.columns:
            common_hours = cluster_data['hour'].mode().values
            if len(common_hours) > 0:
                common_hour = common_hours[0]
                if 6 <= common_hour <= 9:
                    time_char = "morning peak"
                elif 10 <= common_hour <= 16:
                    time_char = "daytime"
                elif 17 <= common_hour <= 21:
                    time_char = "evening peak"
                else:
                    time_char = "off-peak"
                
                return f"{base_char} during {time_char}"
        
        return base_char
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute clustering analysis."""
        return self.analyze(data)

if __name__ == "__main__":
    # Test advanced analytics
    print("📊 Testing advanced analytics plugin...")
    
    # Create sample data
    from datetime import datetime, timedelta
    import random
    
    # Generate sample data
    dates = pd.date_range(start='2024-01-01', end='2024-01-30', freq='h')
    sample_data = []
    
    for date in dates:
        # Simulate realistic consumption patterns
        hour = date.hour
        day_of_week = date.dayofweek
        
        base_consumption = 80
        if 8 <= hour <= 18 and day_of_week < 5:  # Working hours
            base_consumption = 120
        
        # Add randomness
        consumption = base_consumption + random.uniform(-20, 20)
        
        sample_data.append({
            'timestamp': date,
            'energy_consumption': consumption,
            'temperature': 20 + random.uniform(-10, 10),
            'humidity': 50 + random.uniform(-20, 20),
            'occupancy': random.uniform(0, 1)
        })
    
    df = pd.DataFrame(sample_data)
    
    # Test advanced analytics
    analytics_plugin = AdvancedAnalyticsPlugin()
    analytics_plugin.initialize({})
    
    analysis_data = {
        'energy_data': df,
        'building_config': {
            'building_type': 'commercial',
            'floor_area': 2000,
            'building_age': 10
        }
    }
    
    results = analytics_plugin.analyze(analysis_data)
    
    print("✅ Statistical analysis completed")
    print(f"   • Mean consumption: {results['statistical_summary']['descriptive_stats']['mean']:.2f} kWh")
    print(f"   • Efficiency rating: {results['efficiency_metrics']['efficiency_rating']}")
    print(f"   • Anomalies detected: {results['anomaly_detection']['statistical_anomalies']['count']}")
    print(f"   • Recommendations: {len(results['recommendations'])}")
    
    # Test clustering
    clustering_plugin = ClusteringPlugin()
    clustering_plugin.initialize({'n_clusters': 'auto'})
    
    clustering_results = clustering_plugin.analyze(analysis_data)
    print(f"✅ Clustering analysis completed - {clustering_results['optimal_clusters']} clusters found")
    
    print("📊 Advanced analytics test complete!")
