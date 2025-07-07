import requests
import time
import logging
from typing import Dict, List, Optional
import networkx as nx
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

class FeatureService:
    def __init__(self):
        self.base_url = "https://api.blockcypher.com/v1/btc/main"
        self.session = requests.Session()
    
    def extract_features(self, address: str) -> Dict:
        """
        Extract features from a Bitcoin address using BlockCypher API
        Returns the 8 new features used in the ML model with proper data types
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
        """Calculates the 8 new ML features."""
        features = {
            'S5': 0.0, 'S6': 0.0, 'S1-1': 0.0, 'PTIa41-2': 0.0,
            'CI2a32-2': 0.0, 'PTIa21': 0.0, 'PAIa13': 0.0, 'CI3a12-3': 0.0
        }
        
        if not transactions:
            return features
        
        # Build transaction graph
        graph = self._build_transaction_graph(transactions, address)
        
        # Calculate graph-based features (S5, S6, S1-1)
        features.update(self._calculate_graph_features(graph))
        
        # Calculate time-based features
        features.update(self._calculate_time_features(transactions, address))
        
        # Calculate amount-based features
        features.update(self._calculate_amount_features(address_data, transactions, address))
        
        return features
    
    def _build_transaction_graph(self, transactions: List[Dict], target_address: str) -> nx.Graph:
        """Build a graph representation of transactions"""
        graph = nx.Graph()
        
        for tx in transactions:
            if not tx.get('block_time'):
                continue
            
            # Add nodes for all addresses in this transaction
            addresses_in_tx = set()
            
            # Collect input addresses
            for input_tx in tx.get('inputs', []):
                for addr in input_tx.get('addresses', []):
                    addresses_in_tx.add(addr)
                    graph.add_node(addr)
            
            # Collect output addresses
            for output in tx.get('outputs', []):
                for addr in output.get('addresses', []):
                    addresses_in_tx.add(addr)
                    graph.add_node(addr)
            
            # Add edges between all addresses in the same transaction
            addresses_list = list(addresses_in_tx)
            for i in range(len(addresses_list)):
                for j in range(i + 1, len(addresses_list)):
                    graph.add_edge(addresses_list[i], addresses_list[j])
        
        return graph
    
    def _calculate_graph_features(self, graph: nx.Graph) -> Dict:
        """Calculate S5, S6, S1-1 features"""
        features = {'S5': 0.0, 'S6': 0.0, 'S1-1': 0.0}
        
        if len(graph.nodes()) < 2:
            return features
        
        try:
            # S5: Average shortest path length
            if nx.is_connected(graph):
                avg_shortest_path = nx.average_shortest_path_length(graph)
                features['S5'] = round(float(avg_shortest_path), 8)
            else:
                # For disconnected graphs, calculate for largest component
                largest_cc = max(nx.connected_components(graph), key=len)
                if len(largest_cc) > 1:
                    subgraph = graph.subgraph(largest_cc)
                    avg_shortest_path = nx.average_shortest_path_length(subgraph)
                    features['S5'] = round(float(avg_shortest_path), 8)
            
            # S6: Maximum diameter (longest shortest path)
            if nx.is_connected(graph):
                diameter = nx.diameter(graph)
                features['S6'] = int(diameter)
            else:
                # For disconnected graphs, find diameter of largest component
                largest_cc = max(nx.connected_components(graph), key=len)
                if len(largest_cc) > 1:
                    subgraph = graph.subgraph(largest_cc)
                    diameter = nx.diameter(subgraph)
                    features['S6'] = int(diameter)
            
            # S1-1: Average in-degree across all nodes
            in_degrees = [graph.in_degree(node) for node in graph.nodes()]
            avg_in_degree = np.mean(in_degrees) if in_degrees else 0.0
            features['S1-1'] = round(float(avg_in_degree), 8)
            
        except Exception as e:
            logger.error(f"Error calculating graph features: {e}")
        
        return features
    
    def _calculate_time_features(self, transactions: List[Dict], target_address: str) -> Dict:
        """Calculate PTIa41-2, PTIa21 features"""
        features = {'PTIa41-2': 0.0, 'PTIa21': 0.0}
        
        # Sort transactions by time
        valid_transactions = []
        for tx in transactions:
            if tx.get('block_time'):
                valid_transactions.append(tx)
        
        if len(valid_transactions) < 2:
            return features
        
        # Sort by block_time
        valid_transactions.sort(key=lambda x: x['block_time'])
        
        # PTIa41-2: Shortest time interval between consecutive transactions
        time_intervals = []
        for i in range(1, len(valid_transactions)):
            interval = valid_transactions[i]['block_time'] - valid_transactions[i-1]['block_time']
            time_intervals.append(interval)
        
        if time_intervals:
            min_interval = min(time_intervals)
            features['PTIa41-2'] = int(min_interval)
        
        # PTIa21: Ratio of active days to total lifecycle duration
        if len(valid_transactions) >= 2:
            first_time = valid_transactions[0]['block_time']
            last_time = valid_transactions[-1]['block_time']
            total_duration = last_time - first_time
            
            # Count unique active days
            active_days = set()
            for tx in valid_transactions:
                # Convert timestamp to date
                tx_date = datetime.fromtimestamp(tx['block_time']).date()
                active_days.add(tx_date)
            
            active_days_count = len(active_days)
            
            if total_duration > 0:
                # Convert to days
                total_duration_days = total_duration / (24 * 3600)  # seconds to days
                features['PTIa21'] = round(float(active_days_count / total_duration_days), 8)
        
        return features
    
    def _calculate_amount_features(self, address_data: Dict, transactions: List[Dict], target_address: str) -> Dict:
        """Calculate CI2a32-2, PAIa13, CI3a12-3 features"""
        features = {'CI2a32-2': 0.0, 'PAIa13': 0.0, 'CI3a12-3': 0.0}
        
        total_received = float(address_data.get('total_received', 0)) / 100000000.0
        total_sent = float(address_data.get('total_sent', 0)) / 100000000.0
        
        # PAIa13: Ratio between total input and total output amounts
        if total_sent > 0.0:
            features['PAIa13'] = round(total_received / total_sent, 8)
        else:
            features['PAIa13'] = round(total_received, 8) if total_received > 0.0 else 0.0
        
        # CI2a32-2: Highest ratio of change in total input to time interval
        max_ratio = 0.0
        valid_transactions = []
        
        for tx in transactions:
            if tx.get('block_time'):
                valid_transactions.append(tx)
        
        if len(valid_transactions) >= 2:
            valid_transactions.sort(key=lambda x: x['block_time'])
            
            for i in range(1, len(valid_transactions)):
                time_interval = valid_transactions[i]['block_time'] - valid_transactions[i-1]['block_time']
                
                if time_interval > 0:
                    # Calculate input amount for this transaction
                    input_amount = 0.0
                    for input_tx in valid_transactions[i].get('inputs', []):
                        for addr in input_tx.get('addresses', []):
                            if addr == target_address:
                                input_amount += float(input_tx.get('output_value', 0)) / 100000000.0
                    
                    if input_amount > 0:
                        ratio = input_amount / time_interval
                        max_ratio = max(max_ratio, ratio)
        
        features['CI2a32-2'] = round(float(max_ratio), 8)
        
        # CI3a12-3: Lowest number of incoming connections on a single active day
        daily_in_connections = {}
        
        for tx in valid_transactions:
            tx_date = datetime.fromtimestamp(tx['block_time']).date()
            if tx_date not in daily_in_connections:
                daily_in_connections[tx_date] = 0
            
            # Count incoming connections for this transaction
            for input_tx in tx.get('inputs', []):
                for addr in input_tx.get('addresses', []):
                    if addr != target_address:
                        daily_in_connections[tx_date] += 1
        
        if daily_in_connections:
            min_connections = min(daily_in_connections.values())
            features['CI3a12-3'] = int(min_connections)
        
        return features 