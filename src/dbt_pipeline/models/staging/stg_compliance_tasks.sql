-- Materialization profile handled as a view for real-time validation data access
{{ config(materialized='view') }}

SELECT 
    TRIM(task_id) AS task_id,
    LOWER(filename) AS compliance_filename,
    status AS execution_status,
    COALESCE(sentiment_score, 0.0) AS audited_sentiment_score,
    created_at AS ingested_timestamp
FROM 
    compliance_tasks
