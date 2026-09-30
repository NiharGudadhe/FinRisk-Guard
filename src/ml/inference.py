# src/ml/inference.py
import os
import logging
import pickle
import lightgbm as lgb
import numpy as np

# Structured diagnostic logging telemetry configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("FinRisk-ML-Inference")

class FinancialRiskInferenceEngine:
    def __init__(self):
        logger.info("Initializing operational compliance risk inference engine context...")
        self.model_dir = os.path.join("src", "ml", "models")
        self.model_path = os.path.join(self.model_dir, "lightgbm_finrisk.model")
        self.vectorizer_path = os.path.join(self.model_dir, "tfidf_vectorizer.pkl")
        self.encoder_path = os.path.join(self.model_dir, "label_encoder.pkl")
        
        self.model = None
        self.vectorizer = None
        self.encoder = None

    def load_trained_pipeline_artifacts(self):
        """Loads trained weights back from the storage folder into active memory."""
        logger.info("Loading model weights and vectorizer binaries from the models folder...")
        if not os.path.exists(self.model_path):
            logger.warning("Operational error: Trained model weights file missing from folder.")
            return False
            
        try:
            # Safely reload serialized pipeline components natively
            self.model = lgb.Booster(model_file=self.model_path)
            with open(self.vectorizer_path, "rb") as f:
                self.vectorizer = pickle.load(f)
            with open(self.encoder_path, "rb") as f:
                self.encoder = pickle.load(f)
                
            logger.info("All pipeline transformation assets mounted successfully into active runtime memory.")
            return True
        except Exception as e:
            logger.critical(f"Failed to compile memory mount for inference states: {str(e)}")
            return False

    def predict_phrase_risk_sentiment(self, text_phrase: str):
        """Generates real-time compliance validation scores for incoming text queries."""
        if self.model is None or self.vectorizer is None:
            logger.error("Inference halted: Model components are uninitialized.")
            return "UNKNOWN", 0.0

        try:
            # Apply identical TF-IDF text mapping rules
            sparse_vector = self.vectorizer.transform([text_phrase]).toarray()
            prediction_probabilities = self.model.predict(sparse_vector)
            
            # Map index tensors back to human-readable text labels (e.g., negative)
            predicted_index = int(np.argmax(prediction_probabilities, axis=1)[0])
            predicted_label = self.encoder.inverse_transform([predicted_index])[0]
            confidence_score = float(np.max(prediction_probabilities))
            
            logger.info(f"Analysis Pass complete -> Identified: [{predicted_label}] | Confidence: {confidence_score:.4f}")
            return predicted_label, confidence_score
        except Exception as e:
            logger.error(f"Inference array transformation calculations failed: {str(e)}")
            return "ERROR", 0.0

if __name__ == "__main__":
    engine = FinancialRiskInferenceEngine()
    if engine.load_trained_pipeline_artifacts():
        # Execute an isolated liveness check test prediction run
        label, score = engine.predict_phrase_risk_sentiment("Operating profit compressed significantly due to rising raw supply headwinds .")
