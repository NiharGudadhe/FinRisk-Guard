# src/frontend/app.py
import os
import streamlit as st
import httpx
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FinRisk-Frontend-Dashboard")

# Configuration Constants - Point directly to your active local Uvicorn backend loop
BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="FinRisk Guard Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛡️ FinRisk Guard Platform")
st.markdown("### *SEC Compliance & Portfolio Risk Intelligence Control Panel*")
st.divider()

# Sidebar Control Metrics Layout
st.sidebar.header("Infrastructure Node Diagnostics")
if st.sidebar.button("Execute Core Liveness Check"):
    try:
        logger.info("Triggering remote backend diagnostic check request...")
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/health", timeout=3.0)
        
        if response.status_code == 200:
            health_data = response.json()
            st.sidebar.success(f"🟢 Core Node: ONLINE\nEnvironment: {health_data.get('environment')}")
        else:
            st.sidebar.error(f"🔴 Node Degraded: Code {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to resolve socket bridge to backend: {str(e)}")
        st.sidebar.error("🔴 Core Node: UNREACHABLE")

# Main Content Workspace Ingestion Layer
st.header("Document Compliance Auditing Feed")
uploaded_file = st.file_uploader(
    "Stream new SEC Filing, Financial News Corpus or Contract Agreement into the Asynchronous Processing Queue",
    type=["csv", "txt", "pdf"]
)

if uploaded_file is not None:
    if st.button("Initialize Compliance Audit Sequence", type="primary"):
        logger.info(f"Preparing upload stream for asset target: {uploaded_file.name}")
        
        # Prepare files dictionary exactly as expected by FastAPI UploadFile rules
        file_payload = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }
        
        with st.spinner("Streaming data rows natively across local socket networks..."):
            try:
                with httpx.Client() as client:
                    # Fire live online network trigger directly to the FastAPI route layer
                    response = client.post(
                        f"{BACKEND_URL}/api/v1/compliance/analyze", 
                        files=file_payload,
                        timeout=10.0
                    )
                
                if response.status_code == 202:
                    token_data = response.json()
                    st.success("🚀 Ingestion Lifecycle Successful! File locked into MySQL transaction queues.")
                    
                    # Layout modular information tracking panels
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label="Assigned Task Identifier Token", value=token_data.get("task_id")[:13] + "...")
                    with col2:
                        st.metric(label="Current Queue Status Checkpoint", value=token_data.get("status"))
                        
                    logger.info(f"Payload successfully accepted by backend API. Token: {token_data.get('task_id')}")
                else:
                    st.error(f"Ingestion rejected by core api gateway node [{response.status_code}]: {response.text}")
                    
            except Exception as e:
                st.error("Infrastructure Error: Unable to bridge connectivity loop to backend service.")
                logger.critical(f"Frontend failed to reach API gateway over sockets: {str(e)}")
