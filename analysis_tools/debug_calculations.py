import pandas as pd
import numpy as np

# Debug the exchange wallet calculations to identify the issue
print("DEBUGGING EXCHANGE WALLET CALCULATIONS")
print("="*50)

np.random.seed(42)
num_exchanges = 100000

# Current parameters
print("Current parameters:")
print(f"Sent - mean=8.2, sigma=2.0")
print(f"Received - mean=8.5, sigma=2.1")

# Generate with current parameters
exchange_data = {
    'total_sent_btc': np.random.lognormal(mean=8.2, sigma=2.0, size=num_exchanges),
    'total_received_btc': np.random.lognormal(mean=8.5, sigma=2.1, size=num_exchanges),
    'transaction_count': np.random.poisson(lam=5000, size=num_exchanges),
}

df = pd.DataFrame(exchange_data)

print(f"\nCurrent results:")
print(f"Average Sent: {df['total_sent_btc'].mean():.2f} BTC")
print(f"Average Received: {df['total_received_btc'].mean():.2f} BTC")
print(f"Ratio: {df['total_sent_btc'].mean() / df['total_received_btc'].mean():.3f}")

# The issue: lognormal mean parameter is the mean of the LOG, not the actual values
# For lognormal distribution:
# - mean parameter = mean of ln(X)
# - sigma parameter = std of ln(X)
# - Actual mean = exp(mean + sigma^2/2)

print(f"\nLognormal distribution explanation:")
print(f"For Sent (mean=8.2, sigma=2.0):")
print(f"  Actual mean = exp(8.2 + 2.0^2/2) = exp(8.2 + 2.0) = exp(10.2) = {np.exp(10.2):.2f}")

print(f"For Received (mean=8.5, sigma=2.1):")
print(f"  Actual mean = exp(8.5 + 2.1^2/2) = exp(8.5 + 2.205) = exp(10.705) = {np.exp(10.705):.2f}")

# Let's try more balanced parameters
print(f"\nTrying more balanced parameters:")
print(f"Sent - mean=8.0, sigma=1.5")
print(f"Received - mean=8.2, sigma=1.5")

# Reset seed and try new parameters
np.random.seed(42)
exchange_data_balanced = {
    'total_sent_btc': np.random.lognormal(mean=8.0, sigma=1.5, size=num_exchanges),
    'total_received_btc': np.random.lognormal(mean=8.2, sigma=1.5, size=num_exchanges),
    'transaction_count': np.random.poisson(lam=5000, size=num_exchanges),
}

df_balanced = pd.DataFrame(exchange_data_balanced)

print(f"\nBalanced results:")
print(f"Average Sent: {df_balanced['total_sent_btc'].mean():.2f} BTC")
print(f"Average Received: {df_balanced['total_received_btc'].mean():.2f} BTC")
print(f"Ratio: {df_balanced['total_sent_btc'].mean() / df_balanced['total_received_btc'].mean():.3f}")

# Calculate expected values for balanced parameters
print(f"\nExpected values for balanced parameters:")
print(f"For Sent (mean=8.0, sigma=1.5):")
print(f"  Expected mean = exp(8.0 + 1.5^2/2) = exp(8.0 + 1.125) = exp(9.125) = {np.exp(9.125):.2f}")

print(f"For Received (mean=8.2, sigma=1.5):")
print(f"  Expected mean = exp(8.2 + 1.5^2/2) = exp(8.2 + 1.125) = exp(9.325) = {np.exp(9.325):.2f}")

# Let's try even more balanced parameters
print(f"\nTrying very balanced parameters:")
print(f"Sent - mean=8.0, sigma=1.0")
print(f"Received - mean=8.1, sigma=1.0")

np.random.seed(42)
exchange_data_very_balanced = {
    'total_sent_btc': np.random.lognormal(mean=8.0, sigma=1.0, size=num_exchanges),
    'total_received_btc': np.random.lognormal(mean=8.1, sigma=1.0, size=num_exchanges),
    'transaction_count': np.random.poisson(lam=5000, size=num_exchanges),
}

df_very_balanced = pd.DataFrame(exchange_data_very_balanced)

print(f"\nVery balanced results:")
print(f"Average Sent: {df_very_balanced['total_sent_btc'].mean():.2f} BTC")
print(f"Average Received: {df_very_balanced['total_received_btc'].mean():.2f} BTC")
print(f"Ratio: {df_very_balanced['total_sent_btc'].mean() / df_very_balanced['total_received_btc'].mean():.3f}")

print(f"\nExpected values for very balanced parameters:")
print(f"For Sent (mean=8.0, sigma=1.0):")
print(f"  Expected mean = exp(8.0 + 1.0^2/2) = exp(8.0 + 0.5) = exp(8.5) = {np.exp(8.5):.2f}")

print(f"For Received (mean=8.1, sigma=1.0):")
print(f"  Expected mean = exp(8.1 + 1.0^2/2) = exp(8.1 + 0.5) = exp(8.6) = {np.exp(8.6):.2f}")







