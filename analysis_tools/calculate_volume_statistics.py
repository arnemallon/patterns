import pandas as pd
import numpy as np

# Calculate average total volume, input and output of all addresses
print("AVERAGE VOLUME, INPUT AND OUTPUT STATISTICS")
print("="*55)

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

# Calculate overall statistics
avg_total_input = df_volume['total_input'].mean()
avg_total_output = df_volume['total_output'].mean()
avg_total_volume = df_volume['total_volume'].mean()

print(f"\nOVERALL STATISTICS (All Addresses):")
print(f"="*40)
print(f"Average Total Input (Received):  {avg_total_input:.2f} BTC")
print(f"Average Total Output (Sent):     {avg_total_output:.2f} BTC")
print(f"Average Total Volume:            {avg_total_volume:.2f} BTC")

# Calculate additional statistics
median_total_input = df_volume['total_input'].median()
median_total_output = df_volume['total_output'].median()
median_total_volume = df_volume['total_volume'].median()

max_total_input = df_volume['total_input'].max()
max_total_output = df_volume['total_output'].max()
max_total_volume = df_volume['total_volume'].max()

print(f"\nDISTRIBUTION STATISTICS:")
print(f"="*30)
print(f"Median Total Input:    {median_total_input:.2f} BTC")
print(f"Median Total Output:   {median_total_output:.2f} BTC")
print(f"Median Total Volume:   {median_total_volume:.2f} BTC")

print(f"\nMaximum Values:")
print(f"Max Total Input:       {max_total_input:.2f} BTC")
print(f"Max Total Output:      {max_total_output:.2f} BTC")
print(f"Max Total Volume:      {max_total_volume:.2f} BTC")

# Calculate by address type
label_names = {
    0: 'Blackmail', 1: 'Cyber-security', 2: 'Darknet', 3: 'Exchange',
    4: 'P2P Infrastructure', 5: 'P2P Service', 6: 'Gambling',
    7: 'Government', 8: 'Money Laundering', 9: 'Ponzi Scheme',
    10: 'Mining Pool', 11: 'Tumbler', 12: 'Individual'
}

print(f"\nSTATISTICS BY ADDRESS TYPE:")
print(f"="*35)

for label, name in label_names.items():
    if label in df_volume['label'].values:
        subset = df_volume[df_volume['label'] == label]
        
        avg_input = subset['total_input'].mean()
        avg_output = subset['total_output'].mean()
        avg_volume = subset['total_volume'].mean()
        
        print(f"\n{name} (Label {label}):")
        print(f"  Count: {len(subset):,} addresses")
        print(f"  Avg Input:  {avg_input:.2f} BTC")
        print(f"  Avg Output: {avg_output:.2f} BTC")
        print(f"  Avg Volume: {avg_volume:.2f} BTC")
        print(f"  Input/Output Ratio: {avg_input/avg_output:.3f}")

# Summary
print(f"\nSUMMARY:")
print(f"="*15)
print(f"Total addresses analyzed: {len(df_volume):,}")
print(f"Average input across all addresses: {avg_total_input:.2f} BTC")
print(f"Average output across all addresses: {avg_total_output:.2f} BTC")
print(f"Average volume across all addresses: {avg_total_volume:.2f} BTC")
print(f"Net flow (Input - Output): {avg_total_input - avg_total_output:.2f} BTC")







