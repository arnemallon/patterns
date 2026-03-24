import pandas as pd
import numpy as np

# Calculate TOTAL aggregate volume, input and output for EXCHANGE WALLETS ONLY
print("EXCHANGE WALLET TOTAL AGGREGATE STATISTICS")
print("="*50)

# Load real data from BABD13 dataset
data_path = "/Users/arnemallon/Developer/Datasets/BABD-13.csv"
df = pd.read_csv(data_path)

print(f"Loaded {len(df):,} total addresses from BABD13 dataset")

# Filter for EXCHANGE addresses only (label = 3)
exchange_addresses = df[df['label'] == 3].copy()
print(f"Found {len(exchange_addresses):,} exchange addresses")

# Extract volume data from PAI features for exchange addresses only
# PAIa11-1: Output/Sent amounts
# PAIa11-2: Input/Received amounts
exchange_volume_data = {
    'total_input': exchange_addresses['PAIa11-2'].values,    # Total received/input
    'total_output': exchange_addresses['PAIa11-1'].values,   # Total sent/output
}

df_exchange = pd.DataFrame(exchange_volume_data)
df_exchange['total_volume'] = df_exchange['total_input'] + df_exchange['total_output']

# Calculate TOTAL AGGREGATE statistics for exchange wallets only
total_exchange_input = df_exchange['total_input'].sum()
total_exchange_output = df_exchange['total_output'].sum()
total_exchange_volume = df_exchange['total_volume'].sum()

print(f"\nEXCHANGE WALLET TOTAL AGGREGATES:")
print(f"="*40)
print(f"Total Exchange Input (Received):  {total_exchange_input:,.2f} BTC")
print(f"Total Exchange Output (Sent):    {total_exchange_output:,.2f} BTC")
print(f"Total Exchange Volume:           {total_exchange_volume:,.2f} BTC")

# Calculate additional exchange statistics
net_flow = total_exchange_input - total_exchange_output
avg_input_per_exchange = total_exchange_input / len(exchange_addresses)
avg_output_per_exchange = total_exchange_output / len(exchange_addresses)
avg_volume_per_exchange = total_exchange_volume / len(exchange_addresses)

print(f"\nEXCHANGE WALLET ADDITIONAL STATISTICS:")
print(f"="*45)
print(f"Net Flow (Input - Output):       {net_flow:,.2f} BTC")
print(f"Average Input per Exchange:      {avg_input_per_exchange:.2f} BTC")
print(f"Average Output per Exchange:     {avg_output_per_exchange:.2f} BTC")
print(f"Average Volume per Exchange:     {avg_volume_per_exchange:.2f} BTC")

# Distribution statistics for exchange wallets
print(f"\nEXCHANGE WALLET DISTRIBUTION:")
print(f"="*35)
print(f"Min Input per Exchange:          {df_exchange['total_input'].min():.2f} BTC")
print(f"Max Input per Exchange:          {df_exchange['total_input'].max():.2f} BTC")
print(f"Median Input per Exchange:       {df_exchange['total_input'].median():.2f} BTC")
print(f"Min Output per Exchange:         {df_exchange['total_output'].min():.2f} BTC")
print(f"Max Output per Exchange:         {df_exchange['total_output'].max():.2f} BTC")
print(f"Median Output per Exchange:      {df_exchange['total_output'].median():.2f} BTC")
print(f"Min Volume per Exchange:         {df_exchange['total_volume'].min():.2f} BTC")
print(f"Max Volume per Exchange:         {df_exchange['total_volume'].max():.2f} BTC")
print(f"Median Volume per Exchange:      {df_exchange['total_volume'].median():.2f} BTC")

print(f"\nSUMMARY:")
print(f"="*15)
print(f"Total Exchange Addresses: {len(exchange_addresses):,}")
print(f"Total Exchange Input: {total_exchange_input:,.2f} BTC")
print(f"Total Exchange Output: {total_exchange_output:,.2f} BTC")
print(f"Total Exchange Volume: {total_exchange_volume:,.2f} BTC")







