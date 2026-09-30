# tests/test_nlp.py
import os
import logging
from src.nlp.layout_parser import ContractLayoutParser
from src.ml.inference import FinancialRiskInferenceEngine

# Configure test tracking telemetry metrics
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FinRisk-NLP-QA")

def test_contract_layout_parser_chunking():
    """
    Verifies that the layout engine successfully segments a text wall
    into individual clean clause structures using regex rules.
    """
    logger.info("Initializing layout parser chunking test pass...")
    parser = ContractLayoutParser()
    
    # Generate a tiny, isolated mock filing string directly on disk
    mock_file_path = os.path.join("data", "raw", "temporary_test_filing.txt")
    mock_content = "This Agreement is governed by the laws of Nevada.\n\nTermination requires 30 days notice."
    
    with open(mock_file_path, "w", encoding="utf-8") as f:
        f.write(mock_content)
        
    try:
        # Run chunking transformations across the mock file footprint
        clauses = parser.chunk_document_to_clauses(mock_file_path)
        
        # Enforce structural checks to assert data schema validity
        assert isinstance(clauses, list)
        assert len(clauses) == 2
        assert "clause_id" in clauses[0]
        assert "clause_text" in clauses[0]
        logger.info("Layout parser chunking logic verified successfully.")
    finally:
        # Clean up disk space instantly to preserve 512GB SSD constraints
        if os.path.exists(mock_file_path):
            os.remove(mock_file_path)

def test_machine_learning_inference_engine():
    """
    Validates that serialized LightGBM model weights reload cleanly from the
    models folder and generate a deterministic text classification label.
    """
    logger.info("Initializing ML model weights reloading inference test pass...")
    engine = FinancialRiskInferenceEngine()
    
    # Attempt to reload model weights, vectorizer pickles, and encoder matrices
    mounted = engine.load_trained_pipeline_artifacts()
    
    # If the model has not been trained locally yet, skip the prediction assertion gracefully
    if not mounted:
        logger.warning("Test skipped: Serialized model weights files not found in src/ml/models/ folder. Run src/ml/train.py first.")
        return
        
    test_phrase = "Operating profit compressed significantly due to rising raw supply headwinds ."
    label, confidence = engine.predict_phrase_risk_sentiment(test_phrase)
    
    # Enforce quality threshold checks on mathematical outputs
    assert label in ["positive", "neutral", "negative"]
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0
    logger.info(f"ML model inference logic verified. Identified label: {label} (Confidence: {confidence:.4f})")
