import pandas as pd
import numpy as np

# Calculate CORRECT total aggregate volume for exchange wallets using PAIa13
print("CORRECT EXCHANGE WALLET TOTAL AGGREGATE STATISTICS")
print("="*60)

# Load real data from BABD13 dataset
data_path = "/Users/arnemallon/Developer/Datasets/BABD-13.csv"
df = pd.read_csv(data_path)

print(f"Loaded {len(df):,} total addresses from BABD13 dataset")

# Filter for exchange addresses (label = 3)
exchange_addresses = df[df['label'] == 3].copy()
print(f"Found {len(exchange_addresses):,} exchange addresses")

# Use PAIa13 as the main volume feature (this appears to be total volume)
total_exchange_volume = exchange_addresses['PAIa13'].sum()

# Also check if PAIa11-1 and PAIa11-2 are input/output components
total_exchange_input = exchange_addresses['PAIa11-2'].sum()
total_exchange_output = exchange_addresses['PAIa11-1'].sum()

print(f"\nCORRECT EXCHANGE WALLET TOTALS:")
print(f"="*40)
print(f"Total Exchange Volume (PAIa13):    {total_exchange_volume:,.2f} BTC")
print(f"Total Exchange Input (PAIa11-2):   {total_exchange_input:,.2f} BTC")
print(f"Total Exchange Output (PAIa11-1):  {total_exchange_output:,.2f} BTC")

# Calculate per-exchange averages
avg_volume_per_exchange = total_exchange_volume / len(exchange_addresses)
avg_input_per_exchange = total_exchange_input / len(exchange_addresses)
avg_output_per_exchange = total_exchange_output / len(exchange_addresses)

print(f"\nAVERAGE PER EXCHANGE:")
print(f"="*25)
print(f"Average Volume per Exchange:       {avg_volume_per_exchange:.2f} BTC")
print(f"Average Input per Exchange:        {avg_input_per_exchange:.2f} BTC")
print(f"Average Output per Exchange:       {avg_output_per_exchange:.2f} BTC")

# Check the relationship between PAIa13 and PAIa11-1 + PAIa11-2
combined_input_output = total_exchange_input + total_exchange_output
ratio = total_exchange_volume / combined_input_output if combined_input_output > 0 else 0

print(f"\nRELATIONSHIP ANALYSIS:")
print(f"="*25)
print(f"PAIa11-1 + PAIa11-2 total:         {combined_input_output:,.2f} BTC")
print(f"PAIa13 total:                       {total_exchange_volume:,.2f} BTC")
print(f"Ratio (PAIa13 / Combined):         {ratio:.2f}")

# Distribution statistics
print(f"\nEXCHANGE VOLUME DISTRIBUTION:")
print(f"="*35)
pai13_values = exchange_addresses['PAIa13']
print(f"Min Volume per Exchange:           {pai13_values.min():.2f} BTC")
print(f"Max Volume per Exchange:           {pai13_values.max():.2f} BTC")
print(f"Median Volume per Exchange:        {pai13_values.median():.2f} BTC")
print(f"Mean Volume per Exchange:          {pai13_values.mean():.2f} BTC")

print(f"\nSUMMARY:")
print(f"="*15)
print(f"Total Exchange Addresses: {len(exchange_addresses):,}")
print(f"Total Exchange Volume: {total_exchange_volume:,.2f} BTC")
print(f"Average Volume per Exchange: {avg_volume_per_exchange:.2f} BTC")







