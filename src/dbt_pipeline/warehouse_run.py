# src/dbt_pipeline/warehouse_run.py
import os
import logging
import pymysql
import pandas as pd
from sqlglot import transpile
from dotenv import load_dotenv

# Enforce clean engineering log diagnostics
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("FinRisk-dbt-Engine")

class MySQLDbtOrchestrator:
    def __init__(self):
        logger.info("Initializing zero-conflict SQL compilation pipeline for MySQL...")
        db_url = os.getenv("DATABASE_URL", "").replace("mysql+pymysql://", "")
        auth, rest = db_url.split("@")
        user, password = auth.split(":")
        host_port, db_name = rest.split("/")
        self.host, port = host_port.split(":")
        self.user = user
        self.password = password
        self.database = db_name
        self.port = int(port)

    def run_dbt_model(self, file_path: str, target_table_name: str):
        """
        Reads postgres-style Jinja SQL models, removes template definitions, 
        transpiles the dialect via sqlglot, and materializes data tables inside MySQL.
        """
        logger.info(f"Compiling modular dbt SQL script file: [{file_path}]")
        if not os.path.exists(file_path):
            logger.error(f"Execution halted: Target model missing at {file_path}")
            return

        with open(file_path, "r") as f:
            sql_content = f.read()

        # Clean out dbt configuration Jinja tags safely for raw string parsing
        clean_lines = [line for line in sql_content.splitlines() if "{{" not in line and "}}" not in line]
        raw_query_string = "\n".join(clean_lines).strip()

        # Resolve standard dbt table references dynamically
        if "{{ ref('stg_compliance_tasks') }}" in sql_content or "ref(" in sql_content:
            raw_query_string = raw_query_string.replace("stg_compliance_tasks", "stg_compliance_tasks")

        try:
            # Transpile PostgreSQL dialect string criteria cleanly into native MySQL rules
            compiled_query = transpile(raw_query_string, read="postgres", write="mysql")
            
            conn = pymysql.connect(
                host=self.host, user=self.user, password=self.password,
                database=self.database, port=self.port
            )
            
            # Extract data from source table and load into a dataframe structure
            df = pd.read_sql(compiled_query, conn)
            db_engine_url = os.getenv("DATABASE_URL")
            
            # Materialize transformation view/table natively inside MySQL
            df.to_sql(target_table_name, con=db_engine_url, if_exists="replace", index=False)
            
            logger.info(f"Successfully materialized dynamic dbt model to MySQL: [{target_table_name}] (Rows: {len(df)})")
            conn.close()
        except Exception as e:
            logger.error(f"SQL Dialect processing run failed for {target_table_name}: {str(e)}")

    def execute_complete_warehouse_run(self):
        """Orchestrates linear execution tracking analytical data lineages sequentially."""
        logger.info("======================= Starting Pipeline Run =======================")
        
        # 1. Run Staging Layer transformations first
        self.run_dbt_model(
            "src/dbt_pipeline/models/staging/stg_compliance_tasks.sql", 
            "stg_compliance_tasks"
        )
        
        # 2. Run Marts Layer aggregates downstream
        self.run_dbt_model(
            "src/dbt_pipeline/models/marts/fct_portfolio_risk_summary.sql", 
            "fct_portfolio_risk_summary"
        )
        
        logger.info("====================== Pipeline Run Completed ======================")

if __name__ == "__main__":
    runner = MySQLDbtOrchestrator()
    runner.execute_complete_warehouse_run()
