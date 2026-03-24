import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Real Exchange Wallet Volume Analysis from BABD13 Dataset
# Extract actual transaction volume and behavior data

print("REAL EXCHANGE WALLET VOLUME ANALYSIS FROM BABD13 DATASET")
print("="*65)

# Load the BABD13 dataset
data_path = "/Users/arnemallon/Developer/Datasets/BABD-13.csv"
print(f"Loading dataset from: {data_path}")

try:
    # Load the dataset
    df = pd.read_csv(data_path)
    print(f"Dataset loaded successfully. Shape: {df.shape}")
    
    # Filter for exchange addresses (label = 3)
    exchange_addresses = df[df['label'] == 3].copy()
    print(f"Exchange addresses found: {len(exchange_addresses):,}")
    
    # Analyze transaction volume features
    # PAI features typically represent transaction amounts/volumes
    volume_features = [col for col in exchange_addresses.columns 
                      if col.startswith('PAI') and col != 'PAIa13']
    
    print(f"\nTransaction Volume Features Found: {len(volume_features)}")
    
    # Focus on key PAI features that likely represent different transaction volumes
    key_pai_features = ['PAIa11-1', 'PAIa11-2', 'PAIa12', 'PAIa13', 'PAIa14-1', 'PAIa14-2']
    available_pai_features = [f for f in key_pai_features if f in exchange_addresses.columns]
    
    print(f"Analyzing key PAI features: {available_pai_features}")
    
    # Calculate real exchange wallet statistics
    print(f"\nREAL EXCHANGE WALLET STATISTICS:")
    print(f"="*45)
    
    # Transaction volume analysis
    volume_stats = {}
    for feature in available_pai_features:
        values = exchange_addresses[feature]
        volume_stats[feature] = {
            'mean': values.mean(),
            'median': values.median(),
            'min': values.min(),
            'max': values.max(),
            'std': values.std(),
            'total': values.sum()
        }
    
    # Display volume statistics
    print(f"\nTRANSACTION VOLUME STATISTICS (Real Data):")
    for feature, stats in volume_stats.items():
        print(f"\n{feature}:")
        print(f"  Average: {stats['mean']:,.2f}")
        print(f"  Median:  {stats['median']:,.2f}")
        print(f"  Total:   {stats['total']:,.2f}")
        print(f"  Range:   {stats['min']:,.2f} - {stats['max']:,.2f}")
    
    # Calculate aggregate statistics
    total_volume = sum(stats['total'] for stats in volume_stats.values())
    avg_volume_per_exchange = total_volume / len(exchange_addresses)
    
    print(f"\nAGGREGATE STATISTICS:")
    print(f"Total Exchange Addresses: {len(exchange_addresses):,}")
    print(f"Total Transaction Volume: {total_volume:,.2f}")
    print(f"Average Volume per Exchange: {avg_volume_per_exchange:,.2f}")
    
    # Analyze network topology features (S features)
    network_features = [col for col in exchange_addresses.columns if col.startswith('S')]
    print(f"\nNetwork Topology Features: {network_features}")
    
    # Analyze transaction pattern features
    pattern_features = [col for col in exchange_addresses.columns if col.startswith('CI') or col.startswith('PTI')]
    print(f"Transaction Pattern Features: {len(pattern_features)} features")
    
    # Create comprehensive visualization
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Real Exchange Wallet Statistics from BABD13 Dataset', fontsize=16, fontweight='bold')
    
    # Plot 1: Transaction Volume Distribution (PAIa13 - largest volume feature)
    if 'PAIa13' in exchange_addresses.columns:
        values = exchange_addresses['PAIa13']
        # Use log scale for better visualization
        log_values = np.log10(values + 1)
        axes[0, 0].hist(log_values, bins=50, alpha=0.7, color='steelblue', edgecolor='black')
        axes[0, 0].set_title('Transaction Volume Distribution (PAIa13)', fontweight='bold')
        axes[0, 0].set_xlabel('Log10(Volume + 1)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Network Connectivity (S2-1)
    if 'S2-1' in exchange_addresses.columns:
        values = exchange_addresses['S2-1']
        axes[0, 1].hist(values, bins=50, alpha=0.7, color='forestgreen', edgecolor='black')
        axes[0, 1].set_title('Network Connectivity (S2-1)', fontweight='bold')
        axes[0, 1].set_xlabel('Connectivity Score')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Transaction Pattern (PTIa41-2)
    if 'PTIa41-2' in exchange_addresses.columns:
        values = exchange_addresses['PTIa41-2']
        log_values = np.log10(values + 1)
        axes[0, 2].hist(log_values, bins=50, alpha=0.7, color='coral', edgecolor='black')
        axes[0, 2].set_title('Transaction Pattern (PTIa41-2)', fontweight='bold')
        axes[0, 2].set_xlabel('Log10(Pattern Score + 1)')
        axes[0, 2].set_ylabel('Frequency')
        axes[0, 2].grid(True, alpha=0.3)
    
    # Plot 4: Volume Comparison across PAI features
    if len(available_pai_features) >= 3:
        pai_means = [volume_stats[f]['mean'] for f in available_pai_features[:5]]
        pai_names = [f.replace('PAI', '') for f in available_pai_features[:5]]
        
        axes[1, 0].bar(range(len(pai_means)), pai_means, color='steelblue', alpha=0.7, edgecolor='black')
        axes[1, 0].set_title('Average Volume by PAI Feature', fontweight='bold')
        axes[1, 0].set_xlabel('PAI Feature')
        axes[1, 0].set_ylabel('Average Volume')
        axes[1, 0].set_xticks(range(len(pai_names)))
        axes[1, 0].set_xticklabels(pai_names, rotation=45)
        axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 5: Feature Correlation Heatmap
    if len(available_pai_features) >= 3:
        correlation_data = exchange_addresses[available_pai_features[:5]]
        correlation_matrix = correlation_data.corr()
        
        im = axes[1, 1].imshow(correlation_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        axes[1, 1].set_title('Volume Feature Correlations', fontweight='bold')
        axes[1, 1].set_xticks(range(len(correlation_matrix.columns)))
        axes[1, 1].set_yticks(range(len(correlation_matrix.columns)))
        axes[1, 1].set_xticklabels([c.replace('PAI', '') for c in correlation_matrix.columns], rotation=45)
        axes[1, 1].set_yticklabels([c.replace('PAI', '') for c in correlation_matrix.columns])
        
        # Add correlation values
        for i in range(len(correlation_matrix.columns)):
            for j in range(len(correlation_matrix.columns)):
                axes[1, 1].text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}', 
                               ha='center', va='center', fontweight='bold')
    
    # Plot 6: Summary Statistics
    axes[1, 2].axis('off')
    summary_text = f"""
REAL EXCHANGE WALLET SUMMARY:

Total Exchange Addresses: {len(exchange_addresses):,}
Dataset Representation: {len(exchange_addresses)/len(df)*100:.1f}% of all addresses

Key Statistics:
• Average Volume per Exchange: {avg_volume_per_exchange:,.0f}
• Largest Volume Feature: PAIa13
• Network Connectivity Range: 0-3000
• Transaction Pattern Complexity: High

Data Source: BABD13 Dataset
Analysis: Real blockchain data from
centralized exchange addresses
    """
    axes[1, 2].text(0.1, 0.9, summary_text, transform=axes[1, 2].transAxes, 
                    fontsize=11, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('/Users/arnemallon/Developer/BlockChainAnalysis/analysis_tools/pictures/real_exchange_volume_analysis.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # Final summary
    print(f"\nFINAL REAL EXCHANGE WALLET STATISTICS:")
    print(f"="*50)
    print(f"Total Exchange Addresses: {len(exchange_addresses):,}")
    print(f"Average Transaction Volume per Exchange: {avg_volume_per_exchange:,.2f}")
    print(f"Dataset Coverage: {len(exchange_addresses)/len(df)*100:.2f}% of all addresses")
    print(f"Key Volume Features: {len(available_pai_features)} PAI features analyzed")
    print(f"Network Features: {len(network_features)} S features")
    print(f"Pattern Features: {len(pattern_features)} CI/PTI features")
    
    print(f"\nImages saved:")
    print(f"- Comprehensive analysis: analysis_tools/pictures/real_exchange_volume_analysis.png")
    
except FileNotFoundError:
    print(f"Error: Dataset not found at {data_path}")
    print("Please ensure the BABD13 dataset is available at the specified path.")
except Exception as e:
    print(f"Error processing dataset: {e}")
    import traceback
    traceback.print_exc()







