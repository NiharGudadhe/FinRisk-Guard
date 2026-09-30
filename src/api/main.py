@asynccontextmanager
async def database_lifespan_manager(app: FastAPI):
    """
    Handles startup database verification. Caught exceptions are downgraded 
    to warnings to allow the cloud web container to initialize.
    """
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
        # Bypasses the RuntimeError crash to allow Render's port binder to connect
        logger.warning(f"Database connection skipped during startup wrapper: {str(e)}")
        logger.warning("Microservice starting up in headless mock/degraded mode.")
    
    yield
    logger.info("Shutting down microservice server instance...")
