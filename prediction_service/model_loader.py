"""
model_loader.py
---------------
Responsible for loading the pre-trained model and preprocessor .pkl files
from disk at startup. Importing model_class and feature_engineering here
ensures joblib can reconstruct the pickled objects.
"""
import os
import joblib

# These imports are required so joblib can unpickle the .pkl files.
# The classes are not used directly — they are referenced by the pickle metadata.
from model_class import HybridAnomalyDetector              # noqa: F401
from feature_engineering import AdvancedFeatureEngineer    # noqa: F401

BASE_DIR = os.environ.get("PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "models", "model_v1.pkl")
PREPROCESSOR_PATH = os.path.join(BASE_DIR, "models", "preprocessor.pkl")


def load_artifacts():
    """
    Loads and returns (model, preprocessor) from the models/ directory.
    Returns (None, None) if loading fails.
    """
    try:
        model = joblib.load(MODEL_PATH)
        preprocessor = joblib.load(PREPROCESSOR_PATH)
        print("Models loaded successfully.")
        return model, preprocessor
    except Exception as e:
        print(f"Error loading models: {e}")
        return None, None
