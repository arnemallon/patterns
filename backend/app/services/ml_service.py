import tensorflow as tf
import numpy as np
import json
import logging
import sys
from typing import Dict, Optional
import os
import csv

# numpy 2.x renamed numpy.core to numpy._core; the structural model was
# pickled under numpy 2, so alias the old module paths when running under
# numpy 1.x to keep the pickle loadable.
if not hasattr(np, '_core'):
    import numpy.core as _np_core
    sys.modules.setdefault('numpy._core', _np_core)
    for _sub in ('multiarray', 'umath', 'numeric', '_multiarray_umath'):
        _mod = getattr(_np_core, _sub, None)
        if _mod is not None:
            sys.modules.setdefault(f'numpy._core.{_sub}', _mod)

import joblib
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = os.environ.get('PROJECT_ROOT', os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

logger = logging.getLogger(__name__)


class MLService:
    """
    Hybrid classification pipeline as described in the thesis:

    - Addresses contained in our reconstructed transaction graph (the
      structural feature matrix, backend/results/concatenated_features_with_account.csv)
      are classified with the model trained on the top-8 selected BABD-13
      features (S5, S6, S1-1, ...), using the precomputed feature values.
    - All other addresses are classified with the non-structural model, whose
      features are computed on demand from BlockCypher data using the BABD-13
      formulas (see FeatureService).
    """

    # Feature order of the structural model (top-8 selection from the thesis,
    # order verified against og_scaler.joblib and the structural CSV)
    STRUCTURAL_FEATURES = ['S5', 'S6', 'S1-1', 'PTIa41-2', 'CI2a32-2', 'PTIa21', 'PAIa13', 'CI3a12-3']

    # Feature order of the non-structural model (see
    # backend/notebooks/non_strucural_training.ipynb and scaler.json)
    NON_STRUCTURAL_FEATURES = ['S2-1', 'PTIa41-2', 'PTIa41-3', 'S4', 'CI2a32-2', 'PTIa21', 'CI3a12-3', 'PAIa13']

    def __init__(self, model_path: str = None, scaler_path: str = None):
        self.model = None
        self.scaler = None
        self.with_structural_dir = os.path.join(PROJECT_ROOT, 'ml-models/with_structural_features')
        self.without_structural_dir = os.path.join(PROJECT_ROOT, 'ml-models/without_structural_features')
        self.structural_address_csv = os.path.join(
            PROJECT_ROOT, 'backend', 'results', 'concatenated_features_with_account.csv'
        ) if os.path.exists(os.path.join(PROJECT_ROOT, 'backend')) else os.path.join(
            PROJECT_ROOT, 'results', 'concatenated_features_with_account.csv'
        )
        self.structural_features_by_address = None  # address -> feature dict, loaded lazily
        self.models = {}
        self.scalers = {}
        # Load default model and scaler if paths provided (legacy behavior,
        # used by the health check)
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        if scaler_path and os.path.exists(scaler_path):
            self.load_scaler(scaler_path)

    def load_model(self, model_path: str):
        """Load a TensorFlow model (legacy default model slot)"""
        try:
            self.model = self._load_keras_model(model_path)
            logger.info(f"Model loaded successfully from {model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def load_scaler(self, scaler_path: str):
        """Load StandardScaler parameters from a JSON file (legacy default scaler slot)"""
        try:
            self.scaler = self._load_json_scaler(scaler_path)
            logger.info(f"Scaler loaded successfully from {scaler_path}")
        except Exception as e:
            logger.error(f"Error loading scaler: {e}")
            raise

    @staticmethod
    def _load_keras_model(model_path: str):
        model = tf.keras.models.load_model(model_path, compile=False, safe_mode=False)
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        return model

    @staticmethod
    def _load_json_scaler(scaler_path: str) -> StandardScaler:
        with open(scaler_path, 'r') as f:
            scaler_data = json.load(f)
        scaler = StandardScaler()
        scaler.mean_ = np.array(scaler_data['mean'])
        scaler.scale_ = np.array(scaler_data['scale'])
        return scaler

    def _load_structural_features(self):
        """Load the precomputed structural feature matrix (address -> top-8 features)."""
        if self.structural_features_by_address is not None:
            return

        self.structural_features_by_address = {}
        try:
            if not os.path.exists(self.structural_address_csv):
                logger.warning(f"Structural CSV file not found: {self.structural_address_csv}")
                return
            with open(self.structural_address_csv, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    account = (row.get('account') or '').strip()
                    if not account:
                        continue
                    try:
                        self.structural_features_by_address[account] = {
                            name: round(float(row[name]), 8) for name in self.STRUCTURAL_FEATURES
                        }
                    except (KeyError, ValueError):
                        continue
            logger.info(
                f"Loaded structural features for {len(self.structural_features_by_address)} addresses"
            )
        except Exception as e:
            logger.error(f"Failed to load structural features: {e}")
            self.structural_features_by_address = {}

    def get_structural_features(self, address: str) -> Optional[Dict]:
        """
        Return the precomputed structural features for an address, or None if
        the address is not part of our transaction graph or the structural
        model is unavailable.
        """
        if not address:
            return None
        self._load_structural_features()
        features = self.structural_features_by_address.get(address.strip())
        if features is None:
            return None

        model, scaler = self._get_model_and_scaler(use_structural=True)
        if model is None:
            logger.warning("Structural model unavailable, falling back to the non-structural pipeline")
            return None

        logger.info(f"Address {address} found in the transaction graph - using structural model")
        return dict(features)

    def _get_model_and_scaler(self, use_structural: bool):
        """Lazily load and cache the model/scaler pair for a pipeline."""
        key = 'with' if use_structural else 'without'

        if key not in self.models:
            model = None
            scaler = None

            if use_structural:
                model_path = os.path.join(self.with_structural_dir, 'og_bitcoin_classifier.joblib')
                scaler_path = os.path.join(self.with_structural_dir, 'og_scaler.joblib')
                try:
                    if os.path.exists(model_path) and os.path.exists(scaler_path):
                        logger.info(f"Loading structural model from {model_path}")
                        model = joblib.load(model_path)
                        scaler = joblib.load(scaler_path)
                    else:
                        logger.warning(f"Structural model files missing in {self.with_structural_dir}")
                except Exception as e:
                    logger.error(f"Failed to load structural model: {e}")
                    model, scaler = None, None
            else:
                # Prefer .h5 for cross-version compatibility
                model_path_h5 = os.path.join(self.without_structural_dir, 'bitcoin_classifier.h5')
                model_path_keras = os.path.join(self.without_structural_dir, 'bitcoin_classifier.keras')
                model_path = model_path_h5 if os.path.exists(model_path_h5) else model_path_keras
                scaler_path = os.path.join(self.without_structural_dir, 'scaler.json')
                try:
                    if os.path.exists(model_path):
                        logger.info(f"Loading non-structural model from {model_path}")
                        model = self._load_keras_model(model_path)
                    else:
                        logger.warning(f"Non-structural model file missing: {model_path}")
                    if os.path.exists(scaler_path):
                        scaler = self._load_json_scaler(scaler_path)
                    else:
                        logger.warning(f"Non-structural scaler file missing: {scaler_path}")
                except Exception as e:
                    logger.error(f"Failed to load non-structural model: {e}")
                    model, scaler = None, None

            self.models[key] = model
            self.scalers[key] = scaler

        return self.models[key], self.scalers[key]

    def predict(self, features: Dict, address: str = None) -> Dict:
        """
        Classify an address from its feature dict. The pipeline (structural vs.
        non-structural) is determined by which feature set the dict contains.
        """
        use_structural = set(self.STRUCTURAL_FEATURES).issubset(features.keys())
        feature_names = self.STRUCTURAL_FEATURES if use_structural else self.NON_STRUCTURAL_FEATURES

        model, scaler = self._get_model_and_scaler(use_structural)
        if not model:
            raise RuntimeError(
                f"Required model for the {'structural' if use_structural else 'non-structural'} pipeline is missing."
            )

        try:
            feature_array = np.array([[
                float(features.get(name, 0.0)) for name in feature_names
            ]], dtype=np.float64)

            if scaler:
                feature_array = scaler.transform(feature_array)

            if hasattr(model, 'predict_proba'):  # sklearn model (structural)
                probabilities = model.predict_proba(feature_array)[0]
                # The random forest was trained after rare classes were
                # dropped, so map the argmax index back to the class label.
                predicted_class = int(model.classes_[int(np.argmax(probabilities))])
                confidence = float(np.max(probabilities))
                raw_output = probabilities.tolist()
            else:  # keras model (non-structural), outputs logits for 13 classes
                prediction = model.predict(feature_array, verbose=0)
                probabilities = tf.nn.softmax(prediction[0]).numpy()
                predicted_class = int(np.argmax(probabilities))
                confidence = float(np.max(probabilities))
                raw_output = prediction[0].tolist()

            logger.info(
                f"Prediction ({'structural' if use_structural else 'non-structural'}) "
                f"for {address or 'unknown address'}: class={predicted_class}, confidence={confidence:.4f}"
            )

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
