import pandas as pd
import numpy as np

# Investigate PAI features to understand what they actually represent
print("INVESTIGATING PAI FEATURES IN BABD13 DATASET")
print("="*55)

# Load real data from BABD13 dataset
data_path = "/Users/arnemallon/Developer/Datasets/BABD-13.csv"
df = pd.read_csv(data_path)

print(f"Loaded {len(df):,} total addresses from BABD13 dataset")

# Filter for exchange addresses (label = 3)
exchange_addresses = df[df['label'] == 3].copy()
print(f"Found {len(exchange_addresses):,} exchange addresses")

# Get all PAI features
pai_features = [col for col in df.columns if col.startswith('PAI')]
print(f"\nFound {len(pai_features)} PAI features:")
for feature in pai_features:
    print(f"  {feature}")

# Analyze different PAI features for exchange addresses
print(f"\nPAI FEATURE ANALYSIS FOR EXCHANGE ADDRESSES:")
print(f"="*50)

for feature in pai_features:
    values = exchange_addresses[feature]
    print(f"\n{feature}:")
    print(f"  Mean: {values.mean():.6f}")
    print(f"  Median: {values.median():.6f}")
    print(f"  Min: {values.min():.6f}")
    print(f"  Max: {values.max():.6f}")
    print(f"  Sum: {values.sum():.2f}")

# Look for features that might represent larger volumes
print(f"\nSEARCHING FOR HIGH-VOLUME FEATURES:")
print(f"="*40)

# Check all numeric features for exchange addresses
numeric_features = exchange_addresses.select_dtypes(include=[np.number]).columns.tolist()
numeric_features = [f for f in numeric_features if f != 'label']

print(f"Analyzing {len(numeric_features)} numeric features...")

# Find features with highest sums (might indicate volume)
feature_sums = []
for feature in numeric_features:
    total = exchange_addresses[feature].sum()
    if total > 1000000:  # Only show features with significant totals
        feature_sums.append((feature, total))

feature_sums.sort(key=lambda x: x[1], reverse=True)

print(f"\nTop features by total sum (potential volume indicators):")
for feature, total in feature_sums[:20]:
    print(f"  {feature}: {total:,.2f}")

# Check if there are features with very large individual values
print(f"\nFEATURES WITH LARGE INDIVIDUAL VALUES:")
print(f"="*45)

for feature in numeric_features:
    max_val = exchange_addresses[feature].max()
    if max_val > 100000:  # Features with very large max values
        print(f"  {feature}: max = {max_val:,.2f}, mean = {exchange_addresses[feature].mean():.2f}")

# Look specifically at PAIa13 which showed high values earlier
if 'PAIa13' in exchange_addresses.columns:
    print(f"\nDETAILED ANALYSIS OF PAIa13:")
    print(f"="*35)
    pai13_values = exchange_addresses['PAIa13']
    print(f"PAIa13 for exchanges:")
    print(f"  Sum: {pai13_values.sum():,.2f}")
    print(f"  Mean: {pai13_values.mean():.2f}")
    print(f"  Median: {pai13_values.median():.2f}")
    print(f"  Max: {pai13_values.max():.2f}")
    print(f"  Min: {pai13_values.min():.2f}")
    
    # Check if PAIa13 might be the main volume feature
    print(f"\nIf PAIa13 represents volume, total exchange volume would be:")
    print(f"  PAIa13 total: {pai13_values.sum():,.2f} BTC")







