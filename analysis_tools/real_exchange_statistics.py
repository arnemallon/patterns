import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Real Exchange Wallet Statistics from BABD13 Dataset
# Extract actual data from centralized exchange addresses (label = 3)

print("REAL EXCHANGE WALLET STATISTICS FROM BABD13 DATASET")
print("="*60)

# Load the BABD13 dataset
data_path = "/Users/arnemallon/Developer/Datasets/BABD-13.csv"
print(f"Loading dataset from: {data_path}")

try:
    # Load the dataset
    df = pd.read_csv(data_path)
    print(f"Dataset loaded successfully. Shape: {df.shape}")
    
    # Check label distribution
    print(f"\nLabel distribution:")
    label_counts = df['label'].value_counts().sort_index()
    print(label_counts)
    
    # Filter for exchange addresses (label = 3)
    exchange_addresses = df[df['label'] == 3].copy()
    print(f"\nExchange addresses found: {len(exchange_addresses)}")
    
    if len(exchange_addresses) == 0:
        print("No exchange addresses found in the dataset!")
        exit()
    
    # Identify transaction volume features from the dataset
    # Based on the feature selection, these are likely transaction-related features
    volume_features = []
    transaction_features = []
    
    # Look for features that might represent transaction volumes
    for col in exchange_addresses.columns:
        if col not in ['label', 'account'] and pd.api.types.is_numeric_dtype(exchange_addresses[col]):
            # Check if feature name suggests volume or transaction data
            if any(keyword in col.lower() for keyword in ['pai', 'volume', 'amount', 'tx', 'transaction']):
                volume_features.append(col)
            elif any(keyword in col.lower() for keyword in ['count', 'number', 'total']):
                transaction_features.append(col)
    
    print(f"\nIdentified volume-related features: {volume_features}")
    print(f"Identified transaction-related features: {transaction_features}")
    
    # Calculate statistics for exchange addresses
    print(f"\nEXCHANGE WALLET STATISTICS (Real Data from BABD13):")
    print(f"Total Exchange Addresses: {len(exchange_addresses):,}")
    
    # Basic statistics for key features
    print(f"\nKey Statistics for Exchange Addresses:")
    
    # Analyze the top 8 features that were selected in feature selection
    top_features = ['S2-1', 'PTIa41-2', 'PTIa41-3', 'S4', 'CI2a32-2', 'PTIa21', 'CI3a12-3', 'PAIa13']
    
    for feature in top_features:
        if feature in exchange_addresses.columns:
            values = exchange_addresses[feature]
            print(f"\n{feature}:")
            print(f"  Mean: {values.mean():.6f}")
            print(f"  Median: {values.median():.6f}")
            print(f"  Min: {values.min():.6f}")
            print(f"  Max: {values.max():.6f}")
            print(f"  Std: {values.std():.6f}")
    
    # Create visualization of exchange wallet feature distributions
    fig, axes = plt.subplots(2, 4, figsize=(16, 10))
    fig.suptitle('Exchange Wallet Feature Distributions (Real BABD13 Data)', fontsize=16, fontweight='bold')
    
    for i, feature in enumerate(top_features):
        if feature in exchange_addresses.columns and i < 8:
            row = i // 4
            col = i % 4
            
            values = exchange_addresses[feature]
            
            # Use log scale if values are very large
            if values.max() > 1000:
                values_to_plot = np.log10(values + 1)  # Add 1 to avoid log(0)
                axes[row, col].hist(values_to_plot, bins=50, alpha=0.7, color='steelblue', edgecolor='black')
                axes[row, col].set_title(f'{feature} (log10)', fontweight='bold')
                axes[row, col].set_ylabel('Frequency')
            else:
                axes[row, col].hist(values, bins=50, alpha=0.7, color='steelblue', edgecolor='black')
                axes[row, col].set_title(feature, fontweight='bold')
                axes[row, col].set_ylabel('Frequency')
            
            axes[row, col].set_xlabel('Value')
            axes[row, col].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/arnemallon/Developer/BlockChainAnalysis/analysis_tools/pictures/real_exchange_statistics.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # Summary statistics
    print(f"\nSUMMARY STATISTICS FOR EXCHANGE ADDRESSES:")
    print(f"Total Exchange Addresses: {len(exchange_addresses):,}")
    print(f"Dataset represents {len(exchange_addresses)/len(df)*100:.2f}% of all addresses")
    
    # Feature correlation analysis for exchanges
    if len(top_features) > 1:
        exchange_features = exchange_addresses[top_features]
        correlation_matrix = exchange_features.corr()
        
        # Create correlation heatmap
        plt.figure(figsize=(10, 8))
        plt.imshow(correlation_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        plt.colorbar(label='Correlation')
        plt.title('Exchange Wallet Feature Correlations (Real BABD13 Data)', fontweight='bold')
        plt.xticks(range(len(top_features)), top_features, rotation=45)
        plt.yticks(range(len(top_features)), top_features)
        
        # Add correlation values to the heatmap
        for i in range(len(top_features)):
            for j in range(len(top_features)):
                plt.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}', 
                        ha='center', va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/Users/arnemallon/Developer/BlockChainAnalysis/analysis_tools/pictures/exchange_feature_correlations.png',
                    dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
    
    print(f"\nImages saved:")
    print(f"- Real exchange statistics: analysis_tools/pictures/real_exchange_statistics.png")
    print(f"- Feature correlations: analysis_tools/pictures/exchange_feature_correlations.png")
    
except FileNotFoundError:
    print(f"Error: Dataset not found at {data_path}")
    print("Please ensure the BABD13 dataset is available at the specified path.")
except Exception as e:
    print(f"Error processing dataset: {e}")







