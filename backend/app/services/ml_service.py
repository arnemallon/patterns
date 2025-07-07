import tensorflow as tf
import numpy as np
import json
import logging
from typing import Dict, List
import os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
from sklearn.preprocessing import StandardScaler
import csv

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self, model_path: str = None, scaler_path: str = None):
        """
        Initialize ML service with trained model and scaler
        """
        self.model = None
        self.scaler = None
        self.feature_names = [
            'S5', 'S6', 'S1-1', 'PTIa41-2', 'CI2a32-2', 'PTIa21', 
            'PAIa13', 'CI3a12-3'
        ]
        self.with_structural_dir = os.path.join(PROJECT_ROOT, 'ml-models/with_structural_features')
        self.without_structural_dir = os.path.join(PROJECT_ROOT, 'ml-models/without_structural_features')
        self.structural_address_csv = os.path.join(PROJECT_ROOT, 'backend', 'results', 'concatenated_features_with_account.csv')
        self.structural_addresses = None  # Will be loaded as a set
        self.models = {}
        self.scalers = {}
        # Load default model and scaler if paths provided
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        if scaler_path and os.path.exists(scaler_path):
            self.load_scaler(scaler_path)
    
    def load_model(self, model_path: str):
        """Load the trained TensorFlow model"""
        try:
            # Load the model without compiling first to avoid optimizer issues
            self.model = tf.keras.models.load_model(
                model_path,
                compile=False
            )
            
            # Recompile with legacy optimizer for compatibility
            self.model.compile(
                optimizer=tf.keras.optimizers.legacy.Adam(learning_rate=0.001),
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            
            logger.info(f"Model loaded successfully from {model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def load_scaler(self, scaler_path: str):
        """Load the StandardScaler's parameters from a JSON file"""
        try:
            with open(scaler_path, 'r') as f:
                scaler_data = json.load(f)
            
            self.scaler = StandardScaler()
            self.scaler.mean_ = np.array(scaler_data['mean'])
            self.scaler.scale_ = np.array(scaler_data['scale'])

            logger.info(f"Scaler loaded successfully from {scaler_path}")
        except Exception as e:
            logger.error(f"Error loading scaler: {e}")
            raise
    
    def _load_structural_addresses(self):
        if self.structural_addresses is not None:
            return
        self.structural_addresses = set()
        try:
            with open(self.structural_address_csv, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.structural_addresses.add(row['account'].strip())
            print(f"Loaded {len(self.structural_addresses)} addresses from structural CSV")
        except Exception as e:
            # If file is missing or unreadable, treat as empty
            self.structural_addresses = set()
            print(f"Failed to load structural addresses: {e}")

    def _get_model_and_scaler(self, use_structural: bool):
        key = 'with' if use_structural else 'without'
        if key not in self.models or key not in self.scalers:
            model_dir = self.with_structural_dir if use_structural else self.without_structural_dir
            model_path = os.path.join(model_dir, 'bitcoin_classifier.keras')
            scaler_path = os.path.join(model_dir, 'scaler.json')
            logger.debug(f"Checking model path: {model_path}")
            logger.debug(f"Checking scaler path: {scaler_path}")
            model = None
            scaler = None
            if os.path.exists(model_path):
                try:
                    logger.info(f"Loading model from {model_path}")
                    model = tf.keras.models.load_model(model_path, compile=False)
                    model.compile(
                        optimizer=tf.keras.optimizers.legacy.Adam(learning_rate=0.001),
                        loss='sparse_categorical_crossentropy',
                        metrics=['accuracy']
                    )
                    logger.info(f"Model loaded successfully from {model_path}")
                except Exception as e:
                    logger.error(f"Failed to load model from {model_path}: {e}")
                    model = None
            else:
                logger.warning(f"Model file does not exist: {model_path}")
            if os.path.exists(scaler_path):
                try:
                    logger.info(f"Loading scaler from {scaler_path}")
                    with open(scaler_path, 'r') as f:
                        scaler_data = json.load(f)
                    scaler = StandardScaler()
                    scaler.mean_ = np.array(scaler_data['mean'])
                    scaler.scale_ = np.array(scaler_data['scale'])
                    logger.info(f"Scaler loaded successfully from {scaler_path}")
                except Exception as e:
                    logger.error(f"Failed to load scaler from {scaler_path}: {e}")
                    scaler = None
            else:
                logger.warning(f"Scaler file does not exist: {scaler_path}")
            self.models[key] = model
            self.scalers[key] = scaler
        return self.models[key], self.scalers[key]

    def predict(self, features: Dict, address: str = None) -> Dict:
        """
        Make prediction using the correct model based on address presence in the structural CSV
        """
        use_structural = False
        if address:
            self._load_structural_addresses()
            if address.strip() in self.structural_addresses:
                use_structural = True
        print(f"Address {address} is {'in' if use_structural else 'not in'} the structural CSV")
        model, scaler = self._get_model_and_scaler(use_structural)
        try:
            # Convert features dict to array in correct order with proper data types
            feature_array = np.array([[
                float(features.get(name, 0.0)) for name in self.feature_names
            ]], dtype=np.float64)
            
            # Scale features if scaler is available
            if scaler:
                feature_array = scaler.transform(feature_array)
            
            # Make prediction
            if not model:
                raise RuntimeError("Required model for this address type is missing.")
            prediction = model.predict(feature_array, verbose=0)
            # Apply softmax to get probabilities
            probabilities = tf.nn.softmax(prediction[0])
            # Get the predicted class index (0-12)
            predicted_class = int(np.argmax(probabilities))
            # Get the confidence (probability of the predicted class) with high precision
            confidence = float(np.max(probabilities))
            
            logger.info(f"Model raw output: {prediction[0]}")
            logger.info(f"Model probabilities: {probabilities.numpy()}")
            logger.info(f"Predicted class: {predicted_class}")
            logger.info(f"Confidence: {confidence}")
            
            return {
                'prediction': predicted_class,
                'confidence': round(confidence, 8),
                'raw_output': [round(float(x), 8) for x in prediction[0].tolist()],
                'probabilities': [round(float(x), 8) for x in probabilities.numpy().tolist()],
                'features_used': features
            }
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            raise
    
    def _fallback_classification(self, features: Dict) -> Dict:
        """
        Simple fallback classification when model is not loaded
        Based on basic heuristics using the 8 new features with proper data types
        """
        # Simple heuristics based on graph properties and transaction patterns
        avg_shortest_path = float(features.get('S5', 0.0))
        diameter = float(features.get('S6', 0.0))
        avg_in_degree = float(features.get('S1-1', 0.0))
        min_time_interval = float(features.get('PTIa41-2', 0.0))
        max_input_ratio = float(features.get('CI2a32-2', 0.0))
        active_days_ratio = float(features.get('PTIa21', 0.0))
        input_output_ratio = float(features.get('PAIa13', 0.0))
        min_daily_connections = int(features.get('CI3a12-3', 0))
        
        # Simple scoring system based on new features
        score = 0
        
        # High graph complexity might indicate suspicious activity
        if avg_shortest_path > 2.0:
            score += 1
        if diameter > 5:
            score += 1
        
        # High connectivity patterns
        if avg_in_degree > 3.0:
            score += 1
        
        # Very rapid transaction patterns
        if min_time_interval < 3600:  # Less than 1 hour
            score += 2
        
        # High input/output ratios
        if input_output_ratio > 10.0 or input_output_ratio < 0.1:
            score += 1
        
        # High transaction velocity
        if max_input_ratio > 1.0:
            score += 1
        
        # Determine classification based on score
        if score >= 4:
            prediction = 1  # Suspicious
            confidence = 0.8
        elif score >= 2:
            prediction = 1  # Suspicious
            confidence = 0.6
        else:
            prediction = 0  # Normal
            confidence = 0.7
        
        return {
            'prediction': int(prediction),
            'confidence': round(float(confidence), 8),
            'probabilities': [round(float(1-confidence), 8), round(float(confidence), 8)] if prediction == 1 else [round(float(confidence), 8), round(float(1-confidence), 8)],
            'features_used': features,
            'note': 'Using fallback classification (model not loaded)'
        } 