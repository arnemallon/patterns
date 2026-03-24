import pandas as pd
import numpy as np

# Calculate exact values for ALL ADDRESSES from REAL BABD13 dataset
print("EXACT VALUES FROM REAL BABD13 DATASET - ALL ADDRESSES")
print("="*55)

# Load real data from BABD13 dataset
data_path = "/Users/arnemallon/Developer/Datasets/BABD-13.csv"
df = pd.read_csv(data_path)

# Use ALL addresses in the dataset
all_addresses = df.copy()
num_addresses = len(all_addresses)

print(f"Loaded {num_addresses:,} total addresses from BABD13 dataset")

# Check label distribution
label_counts = df['label'].value_counts().sort_index()
print(f"\nLabel distribution:")
for label, count in label_counts.items():
    print(f"  Label {label}: {count:,} addresses")

# Extract real transaction volume data from PAI features for ALL addresses
address_data = {
    'total_sent_btc': all_addresses['PAIa11-1'].values,  # Real sent amounts
    'total_received_btc': all_addresses['PAIa11-2'].values,  # Real received amounts  
    'transaction_count': all_addresses['S2-1'].values,  # Real transaction counts (network connectivity as proxy)
    'label': all_addresses['label'].values  # Keep labels for analysis
}

df_addresses = pd.DataFrame(address_data)
df_addresses['total_volume_btc'] = df_addresses['total_sent_btc'] + df_addresses['total_received_btc']

# Calculate exact values for all addresses
avg_total_sent = df_addresses['total_sent_btc'].mean()
avg_total_received = df_addresses['total_received_btc'].mean()
avg_transaction_count = df_addresses['transaction_count'].mean()
avg_total_volume = df_addresses['total_volume_btc'].mean()

print("\nEXACT VALUES FOR ALL BITCOIN ADDRESSES")
print("(Based on Real BABD13 Dataset)")
print("="*50)
print(f"Average Total Amount Sent FROM All Wallets: {avg_total_sent:.2f} BTC")
print(f"Average Total Amount Sent TO All Wallets:   {avg_total_received:.2f} BTC")
print(f"Average Transaction Count per Address:      {avg_transaction_count:.1f} transactions")
print(f"Average Total Volume per Address:           {avg_total_volume:.2f} BTC")

# Calculate statistics by address type
label_names = {
    0: 'Blackmail', 1: 'Cyber-security', 2: 'Darknet', 3: 'Exchange',
    4: 'P2P Infrastructure', 5: 'P2P Service', 6: 'Gambling',
    7: 'Government', 8: 'Money Laundering', 9: 'Ponzi Scheme',
    10: 'Mining Pool', 11: 'Tumbler', 12: 'Individual'
}

print(f"\nDISTRIBUTION STATISTICS:")
print(f"Total Volume (BTC):")
print(f"  Minimum: {df_addresses['total_volume_btc'].min():.2f} BTC")
print(f"  Maximum: {df_addresses['total_volume_btc'].max():.2f} BTC")
print(f"  Median:  {df_addresses['total_volume_btc'].median():.2f} BTC")
print(f"  Average: {df_addresses['total_volume_btc'].mean():.2f} BTC")

print(f"\nTransaction Count:")
print(f"  Minimum: {df_addresses['transaction_count'].min():.0f} transactions")
print(f"  Maximum: {df_addresses['transaction_count'].max():.0f} transactions")
print(f"  Median:  {df_addresses['transaction_count'].median():.0f} transactions")
print(f"  Average: {df_addresses['transaction_count'].mean():.1f} transactions")

print(f"\nSENT/RECEIVED BREAKDOWN:")
print(f"  Average Sent FROM all addresses: {avg_total_sent:.2f} BTC")
print(f"  Average Sent TO all addresses:   {avg_total_received:.2f} BTC")
print(f"  Ratio (Sent/Received):           {avg_total_sent/avg_total_received:.3f}")

print(f"\nSTATISTICS BY ADDRESS TYPE:")
for label, name in label_names.items():
    if label in df_addresses['label'].values:
        subset = df_addresses[df_addresses['label'] == label]
        print(f"\n{name} (Label {label}):")
        print(f"  Count: {len(subset):,} addresses")
        print(f"  Avg Sent: {subset['total_sent_btc'].mean():.2f} BTC")
        print(f"  Avg Received: {subset['total_received_btc'].mean():.2f} BTC")
        print(f"  Avg Volume: {subset['total_volume_btc'].mean():.2f} BTC")
        print(f"  Avg Transactions: {subset['transaction_count'].mean():.1f}")

print(f"\nSample Size: {num_addresses:,} total Bitcoin addresses")
