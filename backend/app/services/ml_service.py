import tensorflow as tf
import numpy as np
import json
import logging
from typing import Dict, List
import os
PROJECT_ROOT = os.environ.get('PROJECT_ROOT', os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from sklearn.preprocessing import StandardScaler
import csv
import joblib

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
        self.structural_address_csv = os.path.join(
            PROJECT_ROOT, 'backend', 'results', 'concatenated_features_with_account.csv'
        ) if os.path.exists(os.path.join(PROJECT_ROOT, 'backend')) else os.path.join(
            PROJECT_ROOT, 'results', 'concatenated_features_with_account.csv'
        )
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
                compile=False,
                safe_mode=False
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
        """Load addresses from the structural features CSV file"""
        if self.structural_addresses is not None:
            return
        
        self.structural_addresses = set()
        try:
            if os.path.exists(self.structural_address_csv):
                with open(self.structural_address_csv, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'account' in row:
                            self.structural_addresses.add(row['account'].strip())
                logger.info(f"Loaded {len(self.structural_addresses)} addresses from structural CSV")
            else:
                logger.warning(f"Structural CSV file not found: {self.structural_address_csv}")
                self.structural_addresses = set()
        except Exception as e:
            logger.error(f"Failed to load structural addresses: {e}")
            self.structural_addresses = set()

    def _get_model_and_scaler(self, use_structural: bool):
        """Get the appropriate model and scaler based on whether to use structural features"""
        key = 'with' if use_structural else 'without'
        
        if key not in self.models or key not in self.scalers:
            model_dir = self.with_structural_dir if use_structural else self.without_structural_dir
            model = None
            scaler = None
            
            # Try to load model and scaler
            if use_structural:
                # For structural features, try .joblib files first, then .keras
                model_path_joblib = os.path.join(model_dir, 'og_bitcoin_classifier.joblib')
                scaler_path_joblib = os.path.join(model_dir, 'og_scaler.joblib')
                model_path_keras = os.path.join(model_dir, 'bitcoin_classifier.keras')
                scaler_path_json = os.path.join(model_dir, 'scaler.json')
                
                # Try joblib files first
                if os.path.exists(model_path_joblib) and os.path.exists(scaler_path_joblib):
                    try:
                        logger.info(f"Loading joblib model from {model_path_joblib}")
                        model = joblib.load(model_path_joblib)
                        logger.info(f"Loading joblib scaler from {scaler_path_joblib}")
                        scaler = joblib.load(scaler_path_joblib)
                        logger.info("Successfully loaded joblib model and scaler")
                    except Exception as e:
                        logger.error(f"Failed to load joblib files: {e}")
                        logger.info("Falling back to non-structural model due to joblib compatibility issues")
                        # Fall back to non-structural model
                        fallback_dir = self.without_structural_dir
                        model_path = os.path.join(fallback_dir, 'bitcoin_classifier.keras')
                        scaler_path = os.path.join(fallback_dir, 'scaler.json')
                        
                        if os.path.exists(model_path):
                            try:
                                logger.info(f"Loading fallback model from {model_path}")
                                model = tf.keras.models.load_model(model_path, compile=False, safe_mode=False)
                                model.compile(
                                    optimizer=tf.keras.optimizers.legacy.Adam(learning_rate=0.001),
                                    loss='sparse_categorical_crossentropy',
                                    metrics=['accuracy']
                                )
                                logger.info("Fallback model loaded successfully")
                            except Exception as e:
                                logger.error(f"Failed to load fallback model: {e}")
                                model = None
                        
                        if os.path.exists(scaler_path):
                            try:
                                logger.info(f"Loading fallback scaler from {scaler_path}")
                                with open(scaler_path, 'r') as f:
                                    scaler_data = json.load(f)
                                scaler = StandardScaler()
                                scaler.mean_ = np.array(scaler_data['mean'])
                                scaler.scale_ = np.array(scaler_data['scale'])
                                logger.info("Fallback scaler loaded successfully")
                            except Exception as e:
                                logger.error(f"Failed to load fallback scaler: {e}")
                                scaler = None
                
                # Fallback to keras/json files if joblib failed
                if model is None and os.path.exists(model_path_keras):
                    try:
                        logger.info(f"Loading keras model from {model_path_keras}")
                        model = tf.keras.models.load_model(model_path_keras, compile=False, safe_mode=False)
                        model.compile(
                            optimizer=tf.keras.optimizers.legacy.Adam(learning_rate=0.001),
                            loss='sparse_categorical_crossentropy',
                            metrics=['accuracy']
                        )
                        logger.info(f"Keras model loaded successfully")
                    except Exception as e:
                        logger.error(f"Failed to load keras model: {e}")
                        model = None
                
                if scaler is None and os.path.exists(scaler_path_json):
                    try:
                        logger.info(f"Loading json scaler from {scaler_path_json}")
                        with open(scaler_path_json, 'r') as f:
                            scaler_data = json.load(f)
                        scaler = StandardScaler()
                        scaler.mean_ = np.array(scaler_data['mean'])
                        scaler.scale_ = np.array(scaler_data['scale'])
                        logger.info("JSON scaler loaded successfully")
                    except Exception as e:
                        logger.error(f"Failed to load json scaler: {e}")
                        scaler = None
            else:
                # For non-structural features, use keras/json files
                model_path = os.path.join(model_dir, 'bitcoin_classifier.keras')
                scaler_path = os.path.join(model_dir, 'scaler.json')
                
                if os.path.exists(model_path):
                    try:
                        logger.info(f"Loading model from {model_path}")
                        model = tf.keras.models.load_model(model_path, compile=False, safe_mode=False)
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
                logger.info(f"Address {address} found in structural CSV - using structural model")
            else:
                logger.info(f"Address {address} not found in structural CSV - using non-structural model")
        
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
                raise RuntimeError(f"Required model for {'structural' if use_structural else 'non-structural'} features is missing.")
            
            # Handle different model types (joblib vs keras)
            if hasattr(model, 'predict_proba'):  # joblib model (sklearn)
                prediction = model.predict_proba(feature_array)
                probabilities = prediction[0]
                predicted_class = int(np.argmax(probabilities))
                confidence = float(np.max(probabilities))
                raw_output = prediction[0].tolist()
            else:  # keras model
                prediction = model.predict(feature_array, verbose=0)
                # Apply softmax to get probabilities
                probabilities = tf.nn.softmax(prediction[0])
                # Get the predicted class index (0-12)
                predicted_class = int(np.argmax(probabilities))
                # Get the confidence (probability of the predicted class) with high precision
                confidence = float(np.max(probabilities))
                raw_output = prediction[0].tolist()
            
            logger.info(f"Model raw output: {raw_output}")
            logger.info(f"Model probabilities: {probabilities}")
            logger.info(f"Predicted class: {predicted_class}")
            logger.info(f"Confidence: {confidence}")
            
            return {
                'prediction': predicted_class,
                'confidence': round(confidence, 8),
                'raw_output': [round(float(x), 8) for x in raw_output],
                'probabilities': [round(float(x), 8) for x in probabilities],
                'features_used': features,
                'model_type': 'structural' if use_structural else 'non-structural'
            }
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            raise