-- src/dbt_pipeline/models/marts/fct_portfolio_risk_summary.sql
-- Materialized as a physical table to allow lightning-fast Power BI dashboard extraction
{{ config(materialized='table') }}

SELECT 
    COUNT(task_id) AS total_documents_audited,
    ROUND(AVG(audited_sentiment_score), 4) AS average_portfolio_sentiment_index,
    SUM(CASE WHEN audited_sentiment_score < 0.3 THEN 1 ELSE 0 END) AS high_risk_alerts_count,
    MAX(ingested_timestamp) AS last_pipeline_update_timestamp
FROM 
    {{ ref('stg_compliance_tasks') }}
