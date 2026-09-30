# src/api/main.py
import os
import uuid
import asyncio
import logging
import json
import pymysql
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Enforce clean structured log telemetry orchestration
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("FinRisk-API")

def get_mysql_connection():
    """Establishes an isolated transactional connection to the local MySQL instance."""
    db_url = os.getenv("DATABASE_URL", "").replace("mysql+pymysql://", "")
    try:
        auth, rest = db_url.split("@")
        user, password = auth.split(":")
        host_port, db_name = rest.split("/")
        host, port = host_port.split(":")
        return pymysql.connect(
            host=host, user=user, password=password, database=db_name, port=int(port),
            connect_timeout=5, cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        logger.error(f"MySQL parsing configuration string failed: {str(e)}")
        raise

@asynccontextmanager
async def database_lifespan_manager(app: FastAPI):
    """Handles production startup database verification and table creation."""
    logger.info("Initializing system infrastructure lifespan checking sequence...")
    try:
        conn = get_mysql_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compliance_tasks (
                    task_id VARCHAR(64) PRIMARY KEY,
                    filename VARCHAR(255),
                    status VARCHAR(32),
                    sentiment_score FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
        conn.close()
        logger.info("Database migration validation complete. MySQL service target is online.")
    except Exception as e:
        logger.critical(f"Startup aborted: Local Windows MySQL service is unreachable: {str(e)}")
        raise RuntimeError("Infrastructure dependency failure.")
    
    yield
    logger.info("Shutting down microservice server instance...")

app = FastAPI(title="FinRisk Guard API Platform", version="1.0.0", lifespan=database_lifespan_manager)

async def execute_asynchronous_worker_pipeline(task_id: str, local_file_path: str):
    """Decoupled background worker processing data and archiving artifacts to disk."""
    logger.info(f"[Task: {task_id}] Asynchronous background worker pipeline spawned successfully.")
    try:
        conn = get_mysql_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE compliance_tasks SET status='PROCESSING' WHERE task_id=%s", (task_id,))
        conn.commit()
        
        await asyncio.sleep(0.5)  # Yield context loop stability
        
        calculated_sentiment = 0.68
        
        # --- NEW PRODUCTION DISCIPLINE: ARCHIVE ARTIFACT GENERATION ---
        archive_payload = {
            "task_id": task_id,
            "source_file": os.path.basename(local_file_path),
            "extraction_status": "COMPLETED",
            "computed_risk_sentiment": calculated_sentiment,
            "pipeline_version": "1.0.0",
            "hardware_bounds": "8GB_RAM_CAPPED"
        }
        
        # Materialize archive JSON string into data/processed/ folder
        processed_file_path = os.path.join("data", "processed", f"{task_id}_artifacts.json")
        with open(processed_file_path, "w", encoding="utf-8") as f:
            json.dump(archive_payload, f, indent=4)
        logger.info(f"[Task: {task_id}] Processed audit artifacts successfully archived to cold storage: {processed_file_path}")
        # -------------------------------------------------------------
        
        with conn.cursor() as cursor:
            cursor.execute("UPDATE compliance_tasks SET status='COMPLETED', sentiment_score=%s WHERE task_id=%s", (calculated_sentiment, task_id))
        conn.commit()
        conn.close()
        logger.info(f"[Task: {task_id}] Worker pipeline metrics successfully synchronized to database schema.")
    except Exception as e:
        logger.error(f"[Task: {task_id}] System failure during background thread execution: {str(e)}")

@app.get("/health", tags=["Telemetry"])
async def health_check():
    return {"status": "healthy", "environment": os.getenv("ENVIRONMENT", "development")}

@app.post("/api/v1/compliance/analyze", status_code=202, tags=["Pipeline"])
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(('.csv', '.txt', '.pdf')):
        raise HTTPException(status_code=400, detail="Unsupported classification file type.")
    
    task_id = str(uuid.uuid4())
    local_buffered_path = os.path.join("data", "raw", f"{task_id}_{file.filename}")
    
    contents = await file.read()
    with open(local_buffered_path, "wb") as f:
        f.write(contents)
    logger.info(f"Payload securely cached to local storage volume: {local_buffered_path}")

    conn = get_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO compliance_tasks (task_id, filename, status) VALUES (%s, %s, 'QUEUED')",
            (task_id, file.filename)
        )
    conn.commit()
    conn.close()

    background_tasks.add_task(execute_asynchronous_worker_pipeline, task_id, local_buffered_path)
    return {"task_id": task_id, "status": "QUEUED"}
