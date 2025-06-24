import requests
import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class FeatureService:
    def __init__(self):
        self.base_url = "https://api.blockcypher.com/v1/btc/main"
        self.session = requests.Session()
    
    def extract_features(self, address: str) -> Dict:
        """
        Extract features from a Bitcoin address using BlockCypher API
        Returns the 8 features used in the ML model with proper data types
        """
        logger.info(f"Extracting features for address: {address}")
        
        address_data = self._get_address_data(address)
        if not address_data:
            raise Exception("Could not fetch address data")
        
        transactions = self._get_transactions(address)
        
        features = self._calculate_features(address, address_data, transactions)
        
        logger.info(f"Successfully extracted features for {address}")
        return features
            
    def _get_address_data(self, address: str) -> Optional[Dict]:
        """Get basic address information"""
        try:
            response = self.session.get(f"{self.base_url}/addrs/{address}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching address data: {e}")
            return None
    
    def _get_transactions(self, address: str) -> List[Dict]:
        """Get transaction history for the address"""
        try:
            response = self.session.get(f"{self.base_url}/addrs/{address}/full")
            response.raise_for_status()
            data = response.json()
            return data.get('txs', [])
        except requests.RequestException as e:
            logger.error(f"Error fetching transactions: {e}")
            return []
    
    def _calculate_features(self, address: str, address_data: Dict, transactions: List[Dict]) -> Dict:
        """Calculates the 8 ML features."""
        features = {
            'PAIa13': 0.0, 'S2-3': 0, 'CI2a32-2': 0.0, 'CI2a32-4': 0.0,
            'S2-2': 0, 'PAIa11-1': 0.0, 'PAIa11-2': 0.0, 'S2-1': 0
        }
        
        total_received = float(address_data.get('total_received', 0)) / 100000000.0
        total_sent = float(address_data.get('total_sent', 0)) / 100000000.0
        
        features['PAIa11-1'] = round(total_received, 8)
        features['PAIa11-2'] = round(total_sent, 8)
        
        if total_sent > 0.0:
            features['PAIa13'] = round(total_received / total_sent, 8)
        else:
            features['PAIa13'] = round(total_received, 8) if total_received > 0.0 else 0.0
        
        input_addresses, output_addresses = set(), set()
        transaction_changes = []
        
        for tx in transactions:
            if not tx.get('block_time'):
                continue
            
            tx_input_amount, tx_output_amount = 0.0, 0.0
            
            # Using sets to count unique addresses per transaction
            tx_input_addresses, tx_output_addresses = set(), set()

            for input_tx in tx.get('inputs', []):
                for addr in input_tx.get('addresses', []):
                    tx_input_addresses.add(addr)
                    if addr == address:
                        tx_input_amount += float(input_tx.get('output_value', 0)) / 100000000.0
            
            for output in tx.get('outputs', []):
                for addr in output.get('addresses', []):
                    tx_output_addresses.add(addr)
                    if addr == address:
                        tx_output_amount += float(output.get('value', 0)) / 100000000.0
            
            input_addresses.update(tx_input_addresses)
            output_addresses.update(tx_output_addresses)
            
            total_change = tx_input_amount + tx_output_amount
            if total_change > 0.0:
                transaction_changes.append({
                    'input_change': tx_input_amount, 
                    'output_change': tx_output_amount,
                    'total_change': total_change
                })
        
        features['S2-1'] = len(input_addresses)
        features['S2-2'] = len(output_addresses)
        features['S2-3'] = len(input_addresses.union(output_addresses))
        
        max_input_ratio, max_output_ratio = 0.0, 0.0
        if transaction_changes:
            for change in transaction_changes:
                total_change = change['total_change']
                if total_change > 0.0:
                    max_input_ratio = max(max_input_ratio, change['input_change'] / total_change)
                    max_output_ratio = max(max_output_ratio, change['output_change'] / total_change)
        
        features['CI2a32-2'] = round(max_input_ratio, 8)
        features['CI2a32-4'] = round(max_output_ratio, 8)
        
        return features 