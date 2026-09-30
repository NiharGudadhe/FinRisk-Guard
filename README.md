# FinRisk Guard

[![FastAPI Engine](https://shields.io)](https://tiangolo.com)
[![Data Warehouse](https://shields.io)](https://getdbt.com)
[![Database](https://shields.io)](https://mysql.com)
[![Machine Learning](https://shields.io)](https://readthedocs.io)

An asynchronous, decoupled **SEC Compliance & Portfolio Risk Intelligence Data Pipeline** built for high-throughput, low-latency financial text auditing. 

The system natively ingests multi-format regulatory disclosures (SEC 10-K/10-Q, compliance filings, financial news), processes text through an optimized structural NLP layout parser, runs asymmetric risk-sentiment sequence classification via an imbalance-corrected machine learning ensemble, and materializes production-ready data warehouse views using an elite semantic modeling execution layer.

---

## 🏗️ Architectural Overview & Design Patterns

The platform is explicitly built to follow **2026 enterprise microservices trends**, discarding standard flat Jupyter notebooks in favor of production software constraints. It is strictly engineered to run locally with zero-RAM-overhead on a resource-constrained hardware ceiling (**8GB RAM, 512GB SSD**) without memory frame drops or socket degradation.

[ Ingestion Layer ] ──> [ Asynchronous Queue ] ──> [ NLP Feature Core ] ──> [ ML Inference Engine ] ──> [ Transformation Tier ]
Drag-and-Drop       - FastAPI Background      - Regex Layout Parser     - SMOTE Imbalance Fix       - Postgres-Dialect SQL
Multi-Format Stream Worker Tasks    - spaCy Token Cleaner     - Pinned LightGBM Tree       - SQLGlot MySQL Transpiler

### Key Engineering Features:
*   **Asynchronous Background Ingestion:** Eliminates request-response request blockages. Incoming multi-megabyte payloads are instantly written to cold-storage volumes while tracking metadata is spun out into independent thread workers.
*   **Zero-RAM Layout Chunking & Tokenization:** Bypasses heavy local GPU transformer pipelines. Uses high-performance regular expression boundaries and memory-capped `en_core_web_sm` spaCy models to strip structural and linguistic noise.
*   **Imbalance-Corrected Machine Learning Core:** Applies Synthetic Minority Over-sampling (**SMOTE**) alongside an optimized multi-threaded **LightGBM Multiclass Ensemble** to guarantee high precision on rare high-risk alerts.
*   **Zero-Conflict Data Warehousing Layer:** Eliminates native Windows package compilation bottlenecks and Rust/Cargo compiler requirements. Expresses analytical logic in pure, modular **PostgreSQL-style dbt Jinja SQL scripts**, transpiling syntax on the fly to **MySQL** using **SQLGlot**.

---

## 📂 Project Directory Structure

```text
finrisk_guard/
│
├── .github/workflows/
│   └── ci-cd-pipeline.yml      # GitHub Actions CI/CD pipeline automation suite
│
├── data/                       # Local cold-storage data filesystem (Gitignored)
│   ├── raw/                    # Source corpora (financial_phrasebank.csv, sample_filing.pdf)
│   └── processed/              # Materialized structural evaluation historical json logs
│
├── src/                        # Core Application Source Code
│   ├── api/
│   │   └── main.py             # Asynchronous FastAPI backend microservice and lifespan managers
│   ├── nlp/
│   │   ├── layout_parser.py    # Regex structural chunking layout generator
│   │   └── custom_ner.py       # Punctuation/Stopword vocabulary tokenization layer
│   ├── ml/
│   │   ├── models/             # Serialized LightGBM weights and encoder pickles (Gitignored)
│   │   ├── train.py            # Supervised training sequence compiler loops (SMOTE + LightGBM)
│   │   └── inference.py        # Isolated operational live risk sentiment classification model
│   └── dbt_pipeline/
│       ├── models/
│       │   ├── staging/        # [Model: stg_compliance_tasks.sql] Normalization layer
│       │   └── marts/          # [Model: fct_compliance_risk_summary.sql] BI Aggregate Marts
│       └── warehouse_run.py    # Custom semantic dbt-emulation transpilation engine
│
├── tests/                      # Deterministic Quality Assurance Automated Suites
│   ├── test_api.py             # Unit checks evaluating health probes and client routing latencies
│   └── test_nlp.py             # Accuracy checks checking chunking shapes and prediction classes
│
├── .env                        # Local database credentials matrix variables (Gitignored)
├── .gitignore                  # Insulation manifests isolating data volumes/binaries from repository
├── requirements.txt            # Explicitly pinned, CPU-optimized application dependencies
├── render.yaml                 # Infrastructure-as-Code declarative deployment blueprint
└── README.md                   # System configuration and execution manifest
```

---

## 🛠️ Local Installation & Environment Setup

### Prerequisites
*   Windows 11 Operating System
*   Python 3.11.x Runtime Engine
*   Native Local Windows MySQL 8.0 Background Service

### 1. Database Initialization
Log into your local MySQL management client or command line tool and create the project database schema footprint:
```sql
CREATE DATABASE finrisk_db;
```

### 2. Configure Environment Constants
Create an absolute `.env` configuration file inside your root project folder:
```ini
PORT=8000
HOST=127.0.0.1
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/finrisk_db
ENVIRONMENT=development
```

### 3. Initialize Virtual Environment and Sync Dependencies
Open your VS Code terminal window explicitly configured to **Command Prompt (`cmd`)** and execute the installation sequence:
```cmd
:: Initialize native clean venv container
python -m venv venv
.\venv\Scripts\Activate.ps1

:: Force environment wrappers to match the pinned requirements footprints
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

:: Fetch the required vocabulary dependencies natively over the network
python -m spacy download en_core_web_sm
```

---

## 🚀 Step-by-Step Production Execution Pipeline

Follow this sequence exactly to run and validate the complete data lineage loop locally:

### Step 1: Compile the Machine Learning Core Models
Train the multi-class predictive ensemble over your pasted dataset rows. This balance-corrects labels and exports the mathematical weights directly into your `src/ml/models/` folder:
```cmd
python src/ml/train.py
```

### Step 2: Validate Pipeline Logic and Clear QA Gates
Execute the automated `pytest` suite. This spins up the server in memory, checks application routes, and maps inference classification confidence bounds:
```cmd
python -m pytest -v
```

### Step 3: Run the Real-Time Inference Liveness Check
Test the loaded model binaries directly from memory against a custom financial statement to guarantee mathematical output stability:
```cmd
python src/ml/inference.py
```

### Step 4: Boot Up the Live Microservice Engine App Server
Launch the asynchronous network listeners using `uvicorn`:
```cmd
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```
*   Access the live interactive Swagger documentation playground directly inside your web browser at: **`http://localhost:8000/docs`**.

### Step 5: Trigger an Online Ingestion Network Payload
Open a **second, separate terminal window** and call the endpoint natively to stream a financial document data payload over network sockets:
```cmd
python -c "import httpx, os; r = httpx.post('http://localhost:8000/api/v1/compliance/analyze', files={'file': ('financial_phrasebank.csv', open(os.path.join('data', 'raw', 'financial_phrasebank.csv'), 'rb'), 'text/csv')}, timeout=5.0); print(r.json())"
```

### Step 6: Orchestrate Data Warehouse Transformations
Run the custom transpiler model engine to compile your Staging views and Marts aggregate tables directly onto your MySQL instance:
```cmd
python src/dbt_pipeline/warehouse_run.py
```

---

## 🚀 Continuous Integration & Deployment (CI/CD)

The project includes an advanced git-hook automated pipeline configured for the **Render Cloud Infrastructure Platform**.

### GitHub Actions Pipeline (`ci-cd-pipeline.yml`)
Every push or pull request to the `main` or `master` branches automatically spins up a clean Ubuntu Linux virtual machine, attaches Python 3.11, mounts the repository packages, and runs `pytest`. If any code or mapping error is caught, the pipeline fails and freezes deployment immediately to isolate the live servers.

### Render Infrastructure-as-Code (`render.yaml`)
When the continuous integration tests pass successfully, the branch connects to Render's gateway. Render uses the declarative rules defined in the root `render.yaml` blueprint to install dependencies and run `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT` over an open web port natively.

---

# Author
## NIHAR GUDADHE