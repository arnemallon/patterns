#!/usr/bin/env python3
"""
Create Correlation Matrix for the Top 8 Selected Features
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
import os

warnings.filterwarnings('ignore')

def create_top8_correlation_matrix():
    """Create correlation matrix for the top 8 features from our analysis."""
    print("Creating correlation matrix for top 8 features...")
    
    # Load data
    data_path = "/Users/arnemallon/Developer/Datasets/BABD-13.csv"
    df = pd.read_csv(data_path)
    
    # Top 8 features from our feature selection analysis
    top_features = ['S5', 'S6', 'S1-1', 'PTIa41-2', 'CI2a32-2', 'PTIa21', 'PAIa13', 'CI3a12-3']
    
    print(f"Top 8 features: {top_features}")
    
    # Check if all features exist
    missing_features = [f for f in top_features if f not in df.columns]
    if missing_features:
        print(f"Missing features: {missing_features}")
        print("Available features:", df.columns.tolist()[:10])
        return
    
    # Select features and label
    data_for_corr = df[top_features + ['label']].copy()
    
    # Fill missing values
    data_for_corr = data_for_corr.fillna(0)
    
    print(f"Data shape: {data_for_corr.shape}")
    
    # Calculate correlation matrix
    corr_matrix = data_for_corr.corr()
    
    # Create heatmap
    plt.figure(figsize=(10, 8))
    
    # Create mask for upper triangle (optional)
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
    
    # Save to analysis_tools/pictures
    output_dir = "/Users/arnemallon/Developer/BlockChainAnalysis/analysis_tools/pictures"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, "correlation_matrix_top8_features.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Correlation matrix saved to: {output_path}")
    
    # Print correlation values with label
    print("\n" + "="*50)
    print("CORRELATION WITH LABEL")
    print("="*50)
    label_correlations = corr_matrix['label'].drop('label').sort_values(ascending=False)
    for feature, corr in label_correlations.items():
        print(f"{feature:12s}: {corr:6.3f}")
    
    plt.show()

if __name__ == "__main__":
    create_top8_correlation_matrix()






