import requests
import time
import math
import logging
from typing import Dict, List, Optional, Tuple
import networkx as nx
from datetime import datetime, timezone
import numpy as np

logger = logging.getLogger(__name__)

SATOSHI = 100000000.0
SECONDS_PER_DAY = 86400


class FeatureService:
    """
    Computes the feature set of the non-structural model from BlockCypher
    transaction data.

    All formulas replicate the reference implementation in moduleG.py from
    https://github.com/Y-Xiang-hub/Bitcoin-Address-Behavior-Analysis
    (the code that generated the BABD-13 dataset both models were trained on).

    The BABD transaction graph is bipartite: an incoming edge of an address
    node represents one transaction output paying the address (value, time);
    an outgoing edge represents one transaction input spending from it.
    """

    # Feature order of the non-structural model (see
    # backend/notebooks/non_strucural_training.ipynb and scaler.json)
    FEATURE_NAMES = ['S2-1', 'PTIa41-2', 'PTIa41-3', 'S4', 'CI2a32-2', 'PTIa21', 'CI3a12-3', 'PAIa13']

    def __init__(self):
        self.base_url = "https://api.blockcypher.com/v1/btc/main"
        self.session = requests.Session()
        # Cache for API responses to avoid duplicate calls
        self._address_cache = {}
        self._transaction_cache = {}
        self._cache_ttl = 3600  # 1 hour cache

    def extract_features(self, address: str) -> Dict:
        """
        Extract the 8 features of the non-structural model for a Bitcoin
        address using BlockCypher data.
        """
        logger.info(f"Extracting features for address: {address}")

        cached = self.get_cached_data(address)
        if cached is None:
            cached = self.fetch_and_cache_data(address)

        return self._calculate_features(address, cached['address_data'], cached['transactions'])

    def get_cached_data(self, address: str) -> Optional[Dict]:
        """
        Get cached address and transaction data for reuse by other services
        Returns None if data is not cached or expired
        """
        current_time = time.time()

        # Check if we have valid cached data
        if address in self._address_cache and address in self._transaction_cache:
            address_cache_time, address_data = self._address_cache[address]
            tx_cache_time, transactions = self._transaction_cache[address]

            # Check if cache is still valid
            if (current_time - address_cache_time < self._cache_ttl and
                    current_time - tx_cache_time < self._cache_ttl):
                logger.info(f"Returning cached data for {address}")
                return {
                    'address_data': address_data,
                    'transactions': transactions,
                    'cached': True
                }

        return None

    def fetch_and_cache_data(self, address: str) -> Dict:
        """
        Fetch address and transaction data, cache it, and return the data
        This method should be called once per address to populate the cache
        """
        logger.info(f"Fetching and caching data for address: {address}")

        address_data = self._get_address_data(address)
        if not address_data:
            raise Exception("Could not fetch address data")

        transactions = self._get_transactions(address)

        # Cache the data
        current_time = time.time()
        self._address_cache[address] = (current_time, address_data)
        self._transaction_cache[address] = (current_time, transactions)

        return {
            'address_data': address_data,
            'transactions': transactions,
            'cached': False
        }

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

    @staticmethod
    def _tx_timestamp(tx: Dict) -> Optional[int]:
        """Unix timestamp of a confirmed transaction."""
        if tx.get('block_time'):
            return int(tx['block_time'])
        confirmed = tx.get('confirmed')
        if confirmed:
            try:
                dt = datetime.fromisoformat(confirmed.replace('Z', '+00:00'))
                return int(dt.timestamp())
            except ValueError:
                return None
        return None

    def _address_edges(self, address: str, transactions: List[Dict]) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
        """
        Reconstruct the in-/out-edges of the address node as they exist in
        the BABD transaction graph.

        Returns (in_edges, out_edges) where each edge is (timestamp, value in BTC):
        - in_edge:  a transaction output paying the address (tokens received)
        - out_edge: a transaction input spending from the address (tokens sent)
        """
        in_edges = []
        out_edges = []
        for tx in transactions:
            ts = self._tx_timestamp(tx)
            if ts is None:
                continue
            for output in tx.get('outputs', []):
                if address in (output.get('addresses') or []):
                    in_edges.append((ts, float(output.get('value', 0)) / SATOSHI))
            for tx_input in tx.get('inputs', []):
                if address in (tx_input.get('addresses') or []):
                    out_edges.append((ts, float(tx_input.get('output_value', 0)) / SATOSHI))
        return in_edges, out_edges

    def _calculate_features(self, address: str, address_data: Dict, transactions: List[Dict]) -> Dict:
        """Calculate the 8 features of the non-structural model."""
        features = {name: 0.0 for name in self.FEATURE_NAMES}

        logger.info(f"Calculating features for {address} ({len(transactions)} transactions)")

        if not transactions:
            return features

        in_edges, out_edges = self._address_edges(address, transactions)
        all_timestamps = [ts for ts, _ in in_edges] + [ts for ts, _ in out_edges]

        if not all_timestamps:
            return features

        # --- PAIa13 (module_11313): total output amount / total input amount ---
        total_received = sum(value for _, value in in_edges)
        total_sent = sum(value for _, value in out_edges)
        features['PAIa13'] = total_sent / total_received if total_received else 0.0

        # --- PTIa41-2 / PTIa41-3 (module_1314 / module_13141):
        # min/avg interval between unique transaction timestamps, in days ---
        unique_times = sorted(set(all_timestamps))
        if len(unique_times) > 1:
            intervals = [
                (unique_times[i + 1] - unique_times[i]) / SECONDS_PER_DAY
                for i in range(len(unique_times) - 1)
            ]
            features['PTIa41-2'] = min(intervals)
            features['PTIa41-3'] = float(np.mean(intervals))

        # --- PTIa21 (module_13121): life cycle (days) / active period (days) ---
        life_cycle = self._life_cycle_days(all_timestamps)
        active_days = len({self._day_of(ts) for ts in all_timestamps})
        features['PTIa21'] = life_cycle / active_days if active_days else 0.0

        # --- CI2a32-2 (module_14213 / module_142132):
        # max over the series [received amount at t_{i+1} / (t_{i+1} - t_i) * 86400]
        # built from input edges grouped by exact timestamp (BTC per day) ---
        received_per_time = {}
        for ts, value in in_edges:
            received_per_time[ts] = received_per_time.get(ts, 0.0) + value
        received_series = sorted(received_per_time.items())
        if len(received_series) > 1:
            ratios = [
                received_series[i + 1][1] / (received_series[i + 1][0] - received_series[i][0]) * SECONDS_PER_DAY
                for i in range(len(received_series) - 1)
            ]
            features['CI2a32-2'] = max(ratios)

        # --- CI3a12-3 (module_14311 / module_143112):
        # minimum daily in-degree over all active days (days with only
        # outgoing activity count with in-degree 0) ---
        degree_per_day = {}
        for ts, _ in in_edges:
            day = self._day_of(ts)
            degree_per_day.setdefault(day, [0, 0])[0] += 1
        for ts, _ in out_edges:
            day = self._day_of(ts)
            degree_per_day.setdefault(day, [0, 0])[1] += 1
        if degree_per_day:
            features['CI3a12-3'] = float(min(in_deg for in_deg, _ in degree_per_day.values()))

        # --- S2-1 / S4: subgraph structure features ---
        subgraph = self._build_transaction_graph(transactions)
        features['S2-1'] = self._max_in_degree(subgraph)
        features['S4'] = self._betweenness_centrality(subgraph, address)

        features = {key: round(float(value), 8) for key, value in features.items()}
        logger.info(f"Features extracted for {address}: {features}")
        return features

    @staticmethod
    def _day_of(timestamp: int) -> str:
        """Calendar day of a timestamp (module_G formating_timestamp, in UTC)."""
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y%m%d')

    @staticmethod
    def _life_cycle_days(timestamps: List[int]) -> int:
        """Life cycle of the address in solar days (module_1311)."""
        earliest, latest = min(timestamps), max(timestamps)
        if earliest // SECONDS_PER_DAY == latest // SECONDS_PER_DAY:
            return 1
        life_cycle = math.ceil((latest - earliest) / SECONDS_PER_DAY)
        if earliest % SECONDS_PER_DAY >= latest % SECONDS_PER_DAY:
            life_cycle += 1
        return life_cycle

    def _build_transaction_graph(self, transactions: List[Dict]) -> nx.DiGraph:
        """
        Build the directed address-transaction subgraph reachable through the
        address's own transactions (BlockCypher approximation of the BABD
        k-hop subgraph): input address -> transaction -> output address.
        """
        graph = nx.DiGraph()
        for tx in transactions:
            tx_node = ('tx', tx.get('hash'))
            graph.add_node(tx_node, address=False)
            for tx_input in tx.get('inputs', []):
                for addr in (tx_input.get('addresses') or []):
                    graph.add_node(addr, address=True)
                    graph.add_edge(addr, tx_node)
            for output in tx.get('outputs', []):
                for addr in (output.get('addresses') or []):
                    graph.add_node(addr, address=True)
                    graph.add_edge(tx_node, addr)
        return graph

    @staticmethod
    def _max_in_degree(graph: nx.DiGraph) -> float:
        """S2-1 (module_222): maximum in-degree over address nodes of the subgraph."""
        in_degrees = [
            degree for node, degree in graph.in_degree()
            if graph.nodes[node].get('address')
        ]
        return float(max(in_degrees)) if in_degrees else 0.0

    @staticmethod
    def _betweenness_centrality(graph: nx.DiGraph, address: str) -> float:
        """S4 (module_224): normalized betweenness centrality of the address in its subgraph."""
        if address not in graph or graph.number_of_nodes() < 3:
            return 0.0
        try:
            # Sample pivots on large subgraphs to keep the computation fast
            node_count = graph.number_of_nodes()
            k = min(node_count, 500)
            centrality = nx.betweenness_centrality(graph, k=k, normalized=True, seed=42)
            return float(centrality.get(address, 0.0))
        except Exception as e:
            logger.error(f"Error calculating betweenness centrality: {e}")
            return 0.0
