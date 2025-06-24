import tensorflow as tf
import numpy as np
import json
import logging
from typing import Dict, List
import os
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self, model_path: str = None, scaler_path: str = None):
        """
        Initialize ML service with trained model and scaler
        """
        self.model = None
        self.scaler = None
        self.feature_names = [
            'PAIa13', 'S2-3', 'CI2a32-2', 'CI2a32-4', 'S2-2', 
            'PAIa11-1', 'PAIa11-2', 'S2-1'
        ]
        
        # Load model and scaler if paths provided
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
    
    def predict(self, features: Dict) -> Dict:
        """
        Make prediction using the loaded model
        Returns the actual numeric output (0-12) with proper data types
        """
        try:
            # Convert features dict to array in correct order with proper data types
            feature_array = np.array([[
                float(features.get(name, 0.0)) for name in self.feature_names
            ]], dtype=np.float64)
            
            # Scale features if scaler is available
            if self.scaler:
                feature_array = self.scaler.transform(feature_array)
            
            # Make prediction
            if self.model:
                prediction = self.model.predict(feature_array, verbose=0)
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
            else:
                # Fallback: simple rule-based classification
                return self._fallback_classification(features)
                
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            raise
    
    def _fallback_classification(self, features: Dict) -> Dict:
        """
        Simple fallback classification when model is not loaded
        Based on basic heuristics using the 8 available features with proper data types
        """
        # Simple heuristics based on transaction volume and frequency
        total_received = float(features.get('PAIa11-1', 0.0))
        total_sent = float(features.get('PAIa11-2', 0.0))
        n_transactions = int(features.get('S2-1', 0))
        
        # Simple scoring system
        score = 0
        
        # High transaction volume might indicate suspicious activity
        if total_received > 1000.0 or total_sent > 1000.0:
            score += 2
        
        # High transaction frequency
        if n_transactions > 100:
            score += 1
        
        # Large difference between received and sent
        if abs(total_received - total_sent) > 500.0:
            score += 1
        
        # Determine classification based on score
        if score >= 3:
            prediction = 1  # Suspicious
            confidence = 0.7
        elif score >= 1:
            prediction = 1  # Suspicious
            confidence = 0.5
        else:
            prediction = 0  # Normal
            confidence = 0.8
        
        return {
            'prediction': int(prediction),
            'confidence': round(float(confidence), 8),
            'probabilities': [round(float(1-confidence), 8), round(float(confidence), 8)] if prediction == 1 else [round(float(confidence), 8), round(float(1-confidence), 8)],
            'features_used': features,
            'note': 'Using fallback classification (model not loaded)'
        } 