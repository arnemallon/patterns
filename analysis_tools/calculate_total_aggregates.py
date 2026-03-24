import pandas as pd
import numpy as np

# Calculate TOTAL aggregate volume, input and output across ALL addresses
print("TOTAL AGGREGATE VOLUME, INPUT AND OUTPUT STATISTICS")
print("="*60)

# Load real data from BABD13 dataset
data_path = "/Users/arnemallon/Developer/Datasets/BABD-13.csv"
df = pd.read_csv(data_path)

print(f"Loaded {len(df):,} total addresses from BABD13 dataset")

# Extract volume data from PAI features
# PAIa11-1: Output/Sent amounts
# PAIa11-2: Input/Received amounts
volume_data = {
    'total_input': df['PAIa11-2'].values,    # Total received/input
    'total_output': df['PAIa11-1'].values,   # Total sent/output
    'label': df['label'].values
}

df_volume = pd.DataFrame(volume_data)
df_volume['total_volume'] = df_volume['total_input'] + df_volume['total_output']

# Calculate TOTAL AGGREGATE statistics (sum of all addresses)
total_aggregate_input = df_volume['total_input'].sum()
total_aggregate_output = df_volume['total_output'].sum()
total_aggregate_volume = df_volume['total_volume'].sum()

print(f"\nTOTAL AGGREGATE STATISTICS (Sum of All Addresses):")
print(f"="*55)
print(f"Total Aggregate Input (Received):  {total_aggregate_input:,.2f} BTC")
print(f"Total Aggregate Output (Sent):    {total_aggregate_output:,.2f} BTC")
print(f"Total Aggregate Volume:           {total_aggregate_volume:,.2f} BTC")

# Calculate by address type
label_names = {
    0: 'Blackmail', 1: 'Cyber-security', 2: 'Darknet', 3: 'Exchange',
    4: 'P2P Infrastructure', 5: 'P2P Service', 6: 'Gambling',
    7: 'Government', 8: 'Money Laundering', 9: 'Ponzi Scheme',
    10: 'Mining Pool', 11: 'Tumbler', 12: 'Individual'
}

print(f"\nTOTAL AGGREGATES BY ADDRESS TYPE:")
print(f"="*40)

for label, name in label_names.items():
    if label in df_volume['label'].values:
        subset = df_volume[df_volume['label'] == label]
        
        total_input = subset['total_input'].sum()
        total_output = subset['total_output'].sum()
        total_volume = subset['total_volume'].sum()
        
        print(f"\n{name} (Label {label}):")
        print(f"  Count: {len(subset):,} addresses")
        print(f"  Total Input:  {total_input:,.2f} BTC")
        print(f"  Total Output: {total_output:,.2f} BTC")
        print(f"  Total Volume: {total_volume:,.2f} BTC")
        print(f"  Percentage of Total Volume: {(total_volume/total_aggregate_volume)*100:.2f}%")

# Summary
print(f"\nSUMMARY:")
print(f"="*15)
print(f"Total addresses analyzed: {len(df_volume):,}")
print(f"Total aggregate input: {total_aggregate_input:,.2f} BTC")
print(f"Total aggregate output: {total_aggregate_output:,.2f} BTC")
print(f"Total aggregate volume: {total_aggregate_volume:,.2f} BTC")
print(f"Net flow (Input - Output): {total_aggregate_input - total_aggregate_output:,.2f} BTC")

# Calculate what percentage exchange addresses represent
exchange_subset = df_volume[df_volume['label'] == 3]
exchange_total_volume = exchange_subset['total_volume'].sum()
print(f"\nExchange Addresses (Label 3):")
print(f"Exchange Total Volume: {exchange_total_volume:,.2f} BTC")
print(f"Exchange % of Total Volume: {(exchange_total_volume/total_aggregate_volume)*100:.2f}%")







