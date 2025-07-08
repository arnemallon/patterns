from flask import request, jsonify, make_response
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
from sqlalchemy import func

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
        
        # Fetch and cache data for this address (single API call)
        logger.info(f"Fetching and caching data for {address}")
        cached_data = feature_service.fetch_and_cache_data(address)
        
        # Extract features using cached data
        logger.info(f"Extracting features for {address}")
        features = feature_service._calculate_features(
            address, 
            cached_data['address_data'], 
            cached_data['transactions']
        )
        
        # Make prediction
        logger.info(f"Making prediction for {address}")
        prediction_result = ml_service.predict(features, address=address)
        
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

@api.route('/stats', methods=['GET'])
def get_statistics():
    """
    Get dashboard statistics
    Returns counts for addresses analyzed, suspicious addresses, etc.
    """
    try:
        # Get total addresses analyzed
        total_addresses = Classification.query.count()
        
        # Get suspicious addresses (classification = 1)
        suspicious_addresses = Classification.query.filter_by(classification=1).count()
        
        # Get recent activity count (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_activity = Classification.query.filter(Classification.created_at >= yesterday).count()
        
        return jsonify({
            'total_addresses': total_addresses,
            'suspicious_addresses': suspicious_addresses,
            'recent_activity': recent_activity,
            'legitimate_addresses': total_addresses - suspicious_addresses
        })
        
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@api.route('/category-distribution', methods=['GET'])
def get_category_distribution():
    """
    Get category distribution for bar chart
    Returns count of addresses by classification category label
    """
    try:
        # Category mapping (should match frontend)
        categories = [
            'Blackmail', 'Cyber-security Service', 'Darknet Market', 'Centralized Exchange',
            'P2P Financial Infrastructure Service', 'P2P Financial Service', 'Gambling',
            'Government Criminal Blacklist', 'Money Laundering', 'Ponzi Scheme',
            'Mining Pool', 'Tumbler', 'Individual Wallet'
        ]
        # Get count by classification category
        category_counts = db.session.query(
            Classification.classification,
            func.count(Classification.id).label('count')
        ).group_by(Classification.classification).all()
        
        # Convert to dictionary format with label mapping
        distribution = {}
        for category_num, count in category_counts:
            index = int(round(category_num))
            if 0 <= index < len(categories):
                category_name = categories[index]
            else:
                category_name = f'Unknown ({category_num})'
            distribution[category_name] = count
        
        return jsonify(distribution)
        
    except Exception as e:
        logger.error(f"Error fetching category distribution: {str(e)}")
        return jsonify({'error': 'Failed to fetch category distribution'}), 500

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
        
        # Try to get cached data from feature service first
        cached_data = feature_service.get_cached_data(address)
        
        if cached_data:
            logger.info(f"Using cached data from feature service for {address}")
            transactions = cached_data['transactions']
            address_data = cached_data['address_data']
        else:
            # If no cached data, fetch and cache it (this will be used for both features and graph)
            logger.info(f"No cached data found, fetching for {address}")
            cached_data = feature_service.fetch_and_cache_data(address)
            transactions = cached_data['transactions']
            address_data = cached_data['address_data']
        
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
        
    except Exception as e:
        logger.error(f"Error getting transaction graph for {address}: {str(e)}")
        return jsonify({'error': 'Failed to generate transaction graph', 'details': str(e)}), 500

@api.route('/address-count-over-time', methods=['GET'])
def address_count_over_time():
    """
    Returns the number of addresses analyzed per day for the last 30 days.
    """
    try:
        from sqlalchemy import func
        from datetime import datetime, timedelta
        days = 30
        today = datetime.utcnow().date()
        start_date = today - timedelta(days=days-1)

        # Query: count per day
        results = db.session.query(
            func.date(Classification.created_at).label('date'),
            func.count(Classification.id)
        ).filter(
            Classification.created_at >= start_date
        ).group_by(
            func.date(Classification.created_at)
        ).order_by(
            func.date(Classification.created_at)
        ).all()

        # Build a dict with all days in range, fill 0 if missing
        date_counts = {str((start_date + timedelta(days=i))): 0 for i in range(days)}
        for date, count in results:
            date_counts[str(date)] = count

        return jsonify(date_counts)
    except Exception as e:
        logger.error(f"Error fetching address count over time: {str(e)}")
        return jsonify({'error': 'Failed to fetch address count over time'}), 500 

@api.route('/batch-classify', methods=['POST', 'OPTIONS'])
def batch_classify():
    if request.method == 'OPTIONS':
        # CORS preflight
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response, 200
    try:
        data = request.get_json()
        addresses = data.get('addresses', [])
        logger.info(f"Batch classify request received for addresses: {addresses}")
        if not isinstance(addresses, list) or not addresses:
            logger.warning("No addresses provided in batch classify request.")
            return jsonify({'error': 'No addresses provided', 'results': []}), 400
        results = []
        for address in addresses:
            logger.info(f"Processing address: {address}")
            try:
                logger.debug(f"Extracting features for {address}")
                features = feature_service.extract_features(address)
                logger.debug(f"Features for {address}: {features}")
                logger.debug(f"Predicting classification for {address}")
                prediction_result = ml_service.predict(features, address=address)
                logger.debug(f"Prediction result for {address}: {prediction_result}")
                results.append({
                    'address': address,
                    'classification': int(prediction_result['prediction']),
                    'confidence': round(float(prediction_result['confidence']), 8),
                    'status': 'success',
                    'error': None,
                    'cached': False
                })
            except Exception as e:
                logger.error(f"Error classifying address {address}: {str(e)}", exc_info=True)
                results.append({
                    'address': address,
                    'classification': None,
                    'confidence': None,
                    'status': 'error',
                    'error': str(e),
                    'cached': False
                })
            logger.info(f"Result for {address}: {results[-1]}")
        logger.info(f"Batch classify results: {results}")
        response = jsonify({'results': results})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        logger.error(f"Batch classification failed: {str(e)}", exc_info=True)
        response = jsonify({'error': 'Batch classification failed', 'details': str(e), 'results': []})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500 