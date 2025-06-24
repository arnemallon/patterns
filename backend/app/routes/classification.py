from flask import request, jsonify
from app.routes import api
from app.services import FeatureService, MLService
from app.models import Classification
from app import db
import logging
import os
import requests
import json
import hashlib
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Simple in-memory cache for graph data
graph_cache = {}

# --- FIX: Read model paths from environment and initialize services correctly ---
# Get the absolute path of the project's root directory
# This assumes 'run.py' is in a direct subdirectory of the project root, e.g., 'backend/'
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

model_path_from_env = os.getenv('MODEL_PATH')
scaler_path_from_env = os.getenv('SCALER_PATH')

# If the paths from .env are relative, make them absolute based on the project root
model_path = os.path.join(ROOT_DIR, model_path_from_env) if model_path_from_env else None
scaler_path = os.path.join(ROOT_DIR, scaler_path_from_env) if scaler_path_from_env else None

feature_service = FeatureService()
ml_service = MLService(model_path=model_path, scaler_path=scaler_path)

@api.route('/classify', methods=['POST'])
def classify_address():
    """
    Classify a Bitcoin address
    Expected JSON: {"address": "bitcoin_address"}
    """
    try:
        data = request.get_json()
        
        if not data or 'address' not in data:
            return jsonify({'error': 'Address is required'}), 400
        
        address = data['address'].strip()
        
        # Basic validation for Bitcoin address formats (P2PKH, P2SH, and Bech32)
        if not (address.startswith('1') or address.startswith('3') or address.startswith('bc1')) or not (26 <= len(address) <= 90):
            return jsonify({'error': 'Invalid or unsupported Bitcoin address format'}), 400
        
        # Check if we already have this classification in database
        existing = Classification.query.filter_by(address=address).first()
        if existing:
            logger.info(f"Returning cached classification for {address}")
            return jsonify({
                'address': address,
                'classification': int(existing.classification),
                'confidence': round(float(existing.confidence), 8),
                'features': existing.features,
                'created_at': existing.created_at.isoformat(),
                'cached': True
            })
        
        # Extract features
        logger.info(f"Extracting features for {address}")
        features = feature_service.extract_features(address)
        
        # Make prediction
        logger.info(f"Making prediction for {address}")
        prediction_result = ml_service.predict(features)
        
        # Store result in database
        classification_record = Classification(
            address=address,
            classification=int(prediction_result['prediction']),
            confidence=round(float(prediction_result['confidence']), 8),
            features=features
        )
        
        db.session.add(classification_record)
        db.session.commit()
        
        return jsonify({
            'address': address,
            'classification': int(prediction_result['prediction']),
            'confidence': round(float(prediction_result['confidence']), 8),
            'probabilities': [round(float(x), 8) for x in prediction_result.get('probabilities', [])],
            'features': features,
            'note': prediction_result.get('note', ''),
            'cached': False
        })
        
    except Exception as e:
        logger.error(f"Error classifying address: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Classification failed', 'details': str(e)}), 500

@api.route('/history', methods=['GET'])
def get_history():
    """
    Get classification history
    Query params: limit (default 10), offset (default 0)
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get recent classifications
        classifications = Classification.query\
            .order_by(Classification.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        return jsonify({
            'classifications': [c.to_dict() for c in classifications],
            'total': Classification.query.count(),
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        return jsonify({'error': 'Failed to fetch history'}), 500

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'feature_service': 'available',
            'ml_service': 'available' if ml_service.model else 'fallback'
        }
    })

@api.route('/graph/<address>', methods=['GET'])
def get_transaction_graph(address):
    """
    Get transaction graph data for a Bitcoin address
    Returns nodes and edges for visualization
    """
    try:
        logger.info(f"Getting transaction graph for address: {address}")
        
        # Basic validation for Bitcoin address formats
        if not (address.startswith('1') or address.startswith('3') or address.startswith('bc1')) or not (26 <= len(address) <= 90):
            return jsonify({'error': 'Invalid or unsupported Bitcoin address format'}), 400
        
        # Check if the graph data is already cached
        if address in graph_cache:
            logger.info(f"Returning cached graph data for {address}")
            return jsonify(graph_cache[address])
        
        # Get transaction data from BlockCypher API
        # BlockCypher API endpoint for address details
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/full"
        
        logger.info(f"Fetching data from BlockCypher: {url}")
        response = requests.get(url, timeout=30)
        
        logger.info(f"BlockCypher response status: {response.status_code}")
        
        if response.status_code == 429:
            logger.error(f"BlockCypher API rate limited: {response.status_code} - {response.text}")
            return jsonify({
                'error': 'API rate limit reached', 
                'details': 'BlockCypher API rate limit exceeded. Please try again in a few minutes.',
                'nodes': [],
                'edges': [],
                'address': address,
                'transaction_count': 0
            }), 429
        
        if response.status_code != 200:
            logger.error(f"BlockCypher API error: {response.status_code} - {response.text}")
            return jsonify({'error': 'Failed to fetch transaction data', 'details': f'BlockCypher API returned {response.status_code}'}), 500
        
        data = response.json()
        logger.info(f"BlockCypher data received, transactions: {len(data.get('txs', []))}")
        
        # Build graph data
        nodes = []
        edges = []
        
        # Add the main address as a node
        nodes.append({
            'id': address,
            'label': f"{address[:8]}...{address[-8:]}",
            'title': f"Address: {address}",
            'color': '#007bff',
            'size': 25,
            'shape': 'circle',
            'address': address
        })
        
        # Process transactions
        transactions = data.get('txs', [])
        if not transactions:
            logger.info(f"No transactions found for address: {address}")
            result = {
                'nodes': nodes,
                'edges': edges,
                'address': address,
                'transaction_count': 0,
                'message': 'No transactions found for this address'
            }
            # Cache the result for 1 hour
            graph_cache[address] = result
            return jsonify(result)
        
        for tx in transactions[:10]:  # Limit to 10 transactions for performance
            tx_hash = tx['hash']
            logger.debug(f"Processing transaction: {tx_hash}")
            
            # Add transaction as a node
            nodes.append({
                'id': tx_hash,
                'label': f"TX: {tx_hash[:8]}...",
                'title': f"Transaction: {tx_hash}",
                'color': '#28a745',
                'size': 15,
                'shape': 'diamond'
            })
            
            # Add edges from inputs to transaction
            for input_tx in tx.get('inputs', []):
                if 'addresses' in input_tx:
                    for addr in input_tx['addresses']:
                        if addr not in [node['id'] for node in nodes]:
                            nodes.append({
                                'id': addr,
                                'label': f"{addr[:8]}...{addr[-8:]}",
                                'title': f"Address: {addr}",
                                'color': '#ffc107',
                                'size': 20,
                                'shape': 'circle',
                                'address': addr
                            })
                        
                        edges.append({
                            'from': addr,
                            'to': tx_hash,
                            'label': f"{input_tx.get('output_value', 0) / 100000000:.2f} BTC",
                            'title': f"Input: {input_tx.get('output_value', 0) / 100000000:.8f} BTC",
                            'color': '#dc3545',
                            'width': 2,
                            'arrows': 'to'
                        })
            
            # Add edges from transaction to outputs
            for output in tx.get('outputs', []):
                if 'addresses' in output:
                    for addr in output['addresses']:
                        if addr not in [node['id'] for node in nodes]:
                            nodes.append({
                                'id': addr,
                                'label': f"{addr[:8]}...{addr[-8:]}",
                                'title': f"Address: {addr}",
                                'color': '#ffc107',
                                'size': 20,
                                'shape': 'circle',
                                'address': addr
                            })
                        
                        edges.append({
                            'from': tx_hash,
                            'to': addr,
                            'label': f"{output.get('value', 0) / 100000000:.2f} BTC",
                            'title': f"Output: {output.get('value', 0) / 100000000:.8f} BTC",
                            'color': '#28a745',
                            'width': 2,
                            'arrows': 'to'
                        })
        
        logger.info(f"Graph data generated: {len(nodes)} nodes, {len(edges)} edges")
        
        result = {
            'nodes': nodes,
            'edges': edges,
            'address': address,
            'transaction_count': len(transactions)
        }
        
        # Cache the result for 1 hour
        graph_cache[address] = result
        
        return jsonify(result)
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching data from BlockCypher for {address}")
        return jsonify({'error': 'Request timeout', 'details': 'BlockCypher API request timed out'}), 500
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching data from BlockCypher for {address}: {str(e)}")
        return jsonify({'error': 'Network error', 'details': f'Failed to connect to BlockCypher API: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Error getting transaction graph for {address}: {str(e)}")
        return jsonify({'error': 'Failed to generate transaction graph', 'details': str(e)}), 500 