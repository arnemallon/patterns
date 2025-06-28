#!/usr/bin/env python3
"""
Visualize Feature Correlations for Bitcoin Address Classification

This script creates visualizations showing the correlation between the top 8 features
and the target label using seaborn.
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import warnings
import os
from datetime import datetime

warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_data(data_path):
    """Load the dataset and prepare for visualization."""
    print("Loading dataset...")
    data = pd.read_csv(data_path)
    
    # Remove non-numeric columns
    numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
    X = data[numeric_columns].drop('label', axis=1)
    y = data['label']
    
    # Fill missing values
    X = X.fillna(0)
    
    return X, y

def get_top_8_features():
    """Return the top 8 features identified in our analysis."""
    return [
        'S2-1',      # Number of unique input addresses
        'PTIa41-2',  # Transaction pattern indicator (type 2)
        'PTIa41-3',  # Transaction pattern indicator (type 3)
        'S4',        # Network topology complexity metric
        'CI2a32-2',  # Max ratio of input amount to total transaction
        'PTIa21',    # Transaction pattern indicator
        'CI3a12-3',  # Behavioral pattern metric (type 3)
        'PAIa13'     # Ratio of total received to total sent
    ]

def create_correlation_matrix(X, y, top_features):
    """Create correlation matrix for top features and target."""
    print("Creating correlation matrix...")
    
    # Select only the top features
    X_top = X[top_features].copy()
    
    # Add target variable
    data_for_corr = X_top.copy()
    data_for_corr['label'] = y
    
    # Calculate correlation matrix
    corr_matrix = data_for_corr.corr()
    
    return corr_matrix, data_for_corr

def plot_correlation_heatmap(corr_matrix, output_dir="results"):
    """Plot correlation heatmap using seaborn."""
    print("Creating correlation heatmap...")
    
    # Create figure with larger size
    plt.figure(figsize=(12, 10))
    
    # Create mask for upper triangle (optional - to show only lower triangle)
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    
    # Create heatmap
    sns.heatmap(
        corr_matrix,
        mask=mask,
        annot=True,
        cmap='RdBu_r',
        center=0,
        square=True,
        fmt='.3f',
        cbar_kws={"shrink": 0.8},
        linewidths=0.5,
        annot_kws={'size': 10}
    )
    
    plt.title('Feature Correlation Matrix (Top 8 Features + Label)', 
              fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    
    # Save plot
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    heatmap_path = os.path.join(output_dir, f"correlation_heatmap_{timestamp}.png")
    plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
    print(f"Correlation heatmap saved to: {heatmap_path}")
    
    plt.show()

def plot_feature_label_correlations(corr_matrix, output_dir="results"):
    """Plot bar chart of feature correlations with label."""
    print("Creating feature-label correlation plot...")
    
    # Extract correlations with label
    label_correlations = corr_matrix['label'].drop('label').sort_values(ascending=True)
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Create horizontal bar plot
    colors = plt.cm.viridis(np.linspace(0, 1, len(label_correlations)))
    bars = plt.barh(range(len(label_correlations)), label_correlations, color=colors)
    
    # Customize plot
    plt.yticks(range(len(label_correlations)), label_correlations.index)
    plt.xlabel('Correlation with Label', fontsize=12, fontweight='bold')
    plt.title('Feature Correlations with Bitcoin Address Label', 
              fontsize=16, fontweight='bold', pad=20)
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, label_correlations)):
        plt.text(value + (0.01 if value >= 0 else -0.01), 
                bar.get_y() + bar.get_height()/2, 
                f'{value:.3f}', 
                ha='left' if value >= 0 else 'right',
                va='center',
                fontweight='bold')
    
    # Add vertical line at zero
    plt.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    
    # Save plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    corr_plot_path = os.path.join(output_dir, f"feature_label_correlations_{timestamp}.png")
    plt.savefig(corr_plot_path, dpi=300, bbox_inches='tight')
    print(f"Feature-label correlations plot saved to: {corr_plot_path}")
    
    plt.show()

def plot_feature_distributions_by_label(data_for_corr, output_dir="results"):
    """Plot feature distributions grouped by label."""
    print("Creating feature distributions by label...")
    
    # Get top features (excluding label)
    top_features = get_top_8_features()
    
    # Create subplots
    fig, axes = plt.subplots(2, 4, figsize=(20, 12))
    axes = axes.ravel()
    
    for i, feature in enumerate(top_features):
        # Create box plot
        sns.boxplot(data=data_for_corr, x='label', y=feature, ax=axes[i])
        axes[i].set_title(f'{feature} Distribution by Label', fontweight='bold')
        axes[i].set_xlabel('Label')
        axes[i].set_ylabel(feature)
        
        # Rotate x-axis labels for better readability
        axes[i].tick_params(axis='x', rotation=45)
    
    plt.suptitle('Feature Distributions by Bitcoin Address Label', 
                 fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    # Save plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dist_plot_path = os.path.join(output_dir, f"feature_distributions_{timestamp}.png")
    plt.savefig(dist_plot_path, dpi=300, bbox_inches='tight')
    print(f"Feature distributions plot saved to: {dist_plot_path}")
    
    plt.show()

def plot_correlation_network(corr_matrix, output_dir="results"):
    """Plot correlation network graph."""
    print("Creating correlation network plot...")
    
    # Create network-style correlation plot
    plt.figure(figsize=(14, 12))
    
    # Create correlation matrix for network
    corr_network = corr_matrix.copy()
    
    # Create heatmap with different style
    sns.heatmap(
        corr_network,
        annot=True,
        cmap='coolwarm',
        center=0,
        square=True,
        fmt='.2f',
        cbar_kws={"shrink": 0.8},
        linewidths=1,
        annot_kws={'size': 9},
        mask=np.abs(corr_network) < 0.1  # Only show correlations > 0.1
    )
    
    plt.title('Feature Correlation Network (Top 8 Features + Label)', 
              fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    
    # Save plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    network_path = os.path.join(output_dir, f"correlation_network_{timestamp}.png")
    plt.savefig(network_path, dpi=300, bbox_inches='tight')
    print(f"Correlation network plot saved to: {network_path}")
    
    plt.show()

def create_summary_statistics(data_for_corr, output_dir="results"):
    """Create summary statistics for the top features."""
    print("Creating summary statistics...")
    
    top_features = get_top_8_features()
    
    # Calculate summary statistics
    summary_stats = data_for_corr[top_features].describe()
    
    # Add correlation with label
    label_correlations = data_for_corr[top_features].corrwith(data_for_corr['label'])
    summary_stats.loc['correlation_with_label'] = label_correlations
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stats_path = os.path.join(output_dir, f"feature_summary_stats_{timestamp}.csv")
    summary_stats.to_csv(stats_path)
    print(f"Summary statistics saved to: {stats_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("FEATURE SUMMARY STATISTICS")
    print("="*60)
    print(summary_stats.round(4))
    
    return summary_stats

def main():
    """Main function to run all visualizations."""
    # Data path
    data_path = "/Users/arnemallon/Developer/Datasets/BABD-13.csv"
    
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        print("Please ensure the BABD-13.csv file is available.")
        return
    
    # Load data
    X, y = load_data(data_path)
    
    # Get top 8 features
    top_features = get_top_8_features()
    
    # Check if all features exist in the dataset
    missing_features = [f for f in top_features if f not in X.columns]
    if missing_features:
        print(f"Warning: Missing features in dataset: {missing_features}")
        print("Available features:", X.columns.tolist()[:10], "...")
        return
    
    print(f"Using top 8 features: {top_features}")
    
    # Create correlation matrix
    corr_matrix, data_for_corr = create_correlation_matrix(X, y, top_features)
    
    # Create output directory
    output_dir = "results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate all visualizations
    print("\n" + "="*60)
    print("GENERATING VISUALIZATIONS")
    print("="*60)
    
    # 1. Correlation heatmap
    plot_correlation_heatmap(corr_matrix, output_dir)
    
    # 2. Feature-label correlations
    plot_feature_label_correlations(corr_matrix, output_dir)
    
    # 3. Feature distributions by label
    plot_feature_distributions_by_label(data_for_corr, output_dir)
    
    # 4. Correlation network
    plot_correlation_network(corr_matrix, output_dir)
    
    # 5. Summary statistics
    summary_stats = create_summary_statistics(data_for_corr, output_dir)
    
    print("\n" + "="*60)
    print("VISUALIZATION COMPLETE")
    print("="*60)
    print("All plots have been saved to the 'results' directory.")
    print("Check the generated PNG files for detailed visualizations.")

if __name__ == "__main__":
    main() 