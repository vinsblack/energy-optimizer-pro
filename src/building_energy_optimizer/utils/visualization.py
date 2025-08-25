"""
Basic visualization utilities for Building Energy Optimizer.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any

def create_basic_plot(data: pd.DataFrame, title: str = "Energy Data") -> None:
    """Create basic energy consumption plot."""
    plt.figure(figsize=(12, 6))
    if 'timestamp' in data.columns and 'energy_consumption' in data.columns:
        plt.plot(data['timestamp'], data['energy_consumption'])
        plt.title(title)
        plt.xlabel('Time')
        plt.ylabel('Energy Consumption (kWh)')
        plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def create_correlation_matrix(data: pd.DataFrame) -> None:
    """Create correlation matrix heatmap."""
    numeric_cols = data.select_dtypes(include=[float, int]).columns
    if len(numeric_cols) > 1:
        corr_matrix = data[numeric_cols].corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('Feature Correlation Matrix')
        plt.tight_layout()
        plt.show()

def plot_predictions_vs_actual(y_true, y_pred, title: str = "Predictions vs Actual") -> None:
    """Plot predictions against actual values."""
    plt.figure(figsize=(8, 6))
    plt.scatter(y_true, y_pred, alpha=0.5)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
    plt.xlabel('Actual Values')
    plt.ylabel('Predicted Values')
    plt.title(title)
    plt.tight_layout()
    plt.show()

def create_energy_dashboard_plots(data: pd.DataFrame) -> Dict[str, Any]:
    """Create comprehensive energy analysis plots."""
    plots_info = {}
    
    # Time series plot
    if 'timestamp' in data.columns and 'energy_consumption' in data.columns:
        plt.figure(figsize=(12, 6))
        plt.plot(data['timestamp'], data['energy_consumption'])
        plt.title('Energy Consumption Over Time')
        plt.xlabel('Time')
        plt.ylabel('Energy Consumption (kWh)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plots_info['timeseries'] = 'Energy consumption timeline'
    
    return plots_info

def save_plot_to_file(filename: str = "energy_plot.png") -> None:
    """Save current plot to file."""
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Plot saved to {filename}")

# Export functions
__all__ = [
    'create_basic_plot',
    'create_correlation_matrix', 
    'plot_predictions_vs_actual',
    'create_energy_dashboard_plots',
    'save_plot_to_file'
]