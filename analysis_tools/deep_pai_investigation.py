import pandas as pd
import numpy as np

# Deep investigation of what PAI features actually represent
print("DEEP INVESTIGATION OF PAI FEATURES")
print("="*40)

# Load real data from BABD13 dataset
data_path = "/Users/arnemallon/Developer/Datasets/BABD-13.csv"
df = pd.read_csv(data_path)

print(f"Loaded {len(df):,} total addresses from BABD13 dataset")

# Filter for exchange addresses (label = 3)
exchange_addresses = df[df['label'] == 3].copy()
print(f"Found {len(exchange_addresses):,} exchange addresses")

# Look at the distribution of PAIa13 more carefully
pai13_values = exchange_addresses['PAIa13']
print(f"\nPAIa13 DETAILED ANALYSIS:")
print(f"="*30)
print(f"Total sum: {pai13_values.sum():,.2f}")
print(f"Mean: {pai13_values.mean():.6f}")
print(f"Median: {pai13_values.median():.6f}")
print(f"Min: {pai13_values.min():.6f}")
print(f"Max: {pai13_values.max():.6f}")

# Check what percentage of addresses have very large values
print(f"\nPAIa13 DISTRIBUTION ANALYSIS:")
print(f"="*35)
print(f"Addresses with PAIa13 = 0: {(pai13_values == 0).sum():,} ({(pai13_values == 0).mean()*100:.1f}%)")
print(f"Addresses with PAIa13 < 1: {(pai13_values < 1).sum():,} ({(pai13_values < 1).mean()*100:.1f}%)")
print(f"Addresses with PAIa13 < 10: {(pai13_values < 10).sum():,} ({(pai13_values < 10).mean()*100:.1f}%)")
print(f"Addresses with PAIa13 >= 1000: {(pai13_values >= 1000).sum():,} ({(pai13_values >= 1000).mean()*100:.1f}%)")
print(f"Addresses with PAIa13 >= 10000: {(pai13_values >= 10000).sum():,} ({(pai13_values >= 10000).mean()*100:.1f}%)")

# Look at the top addresses by PAIa13
print(f"\nTOP 10 EXCHANGE ADDRESSES BY PAIa13:")
print(f"="*45)
top_addresses = exchange_addresses.nlargest(10, 'PAIa13')[['PAIa13', 'PAIa11-1', 'PAIa11-2']]
for i, (idx, row) in enumerate(top_addresses.iterrows(), 1):
    print(f"{i:2d}. PAIa13: {row['PAIa13']:,.2f}, PAIa11-1: {row['PAIa11-1']:,.2f}, PAIa11-2: {row['PAIa11-2']:,.2f}")

# Check if PAIa13 might be in a different unit or scale
print(f"\nSCALING ANALYSIS:")
print(f"="*20)

# Maybe PAIa13 is in satoshis instead of BTC?
pai13_satoshis = pai13_values / 100000000  # Convert to BTC if it's in satoshis
print(f"If PAIa13 is in satoshis:")
print(f"  Total in BTC: {pai13_satoshis.sum():,.2f} BTC")
print(f"  Average per exchange: {pai13_satoshis.mean():.2f} BTC")

# Maybe it's in a different scale?
print(f"\nIf PAIa13 is divided by 1000:")
pai13_scaled = pai13_values / 1000
print(f"  Total: {pai13_scaled.sum():,.2f} BTC")
print(f"  Average per exchange: {pai13_scaled.mean():.2f} BTC")

# Compare with other address types to see if this makes sense
print(f"\nCOMPARISON WITH OTHER ADDRESS TYPES:")
print(f"="*45)

for label in [0, 1, 2, 6, 12]:  # Check a few other types
    subset = df[df['label'] == label]
    if len(subset) > 0:
        pai13_total = subset['PAIa13'].sum()
        pai13_avg = subset['PAIa13'].mean()
        label_name = ['Blackmail', 'Cyber-security', 'Darknet', 'Gambling', 'Individual'][label if label < 6 else 4]
        print(f"{label_name}: {len(subset):,} addresses, PAIa13 total: {pai13_total:,.2f}, avg: {pai13_avg:.2f}")

# Check what the feature documentation might tell us
print(f"\nFEATURE RELATIONSHIP ANALYSIS:")
print(f"="*35)
print(f"PAIa13 vs PAIa11-1 + PAIa11-2:")
print(f"  PAIa13 total: {pai13_values.sum():,.2f}")
print(f"  PAIa11-1 total: {exchange_addresses['PAIa11-1'].sum():,.2f}")
print(f"  PAIa11-2 total: {exchange_addresses['PAIa11-2'].sum():,.2f}")
print(f"  PAIa11-1 + PAIa11-2: {(exchange_addresses['PAIa11-1'].sum() + exchange_addresses['PAIa11-2'].sum()):,.2f}")

# Maybe PAIa13 is cumulative or represents something different
print(f"\nPOSSIBLE INTERPRETATIONS:")
print(f"="*30)
print(f"1. PAIa13 might be cumulative volume over time")
print(f"2. PAIa13 might include internal transfers")
print(f"3. PAIa13 might be in different units (satoshis, mBTC, etc.)")
print(f"4. PAIa13 might represent a different metric entirely")







