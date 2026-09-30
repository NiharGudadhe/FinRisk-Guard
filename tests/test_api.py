# tests/test_api.py
import logging
from fastapi.testclient import TestClient
from src.api.main import app

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FinRisk-QA-Testing")

def test_api_health_endpoint_liveness():
    """
    Verifies that the API health monitoring checks return 
    healthy status metrics after full application initialization.
    """
    logger.info("Instantiating isolated application context runner client...")
    # Creating the runtime wrapper inside the block resolves router registration timing issues
    with TestClient(app) as client:
        logger.info("Triggering automated platform liveness unit checks...")
        response = client.get("/health")
        
        # Enforce truth assertion checks
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        logger.info("Liveness testing evaluation passed. API health probe is completely stable.")
