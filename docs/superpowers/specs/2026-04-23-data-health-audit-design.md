# Spec: Comprehensive Data and Storage Audit Tool

## Context
BetWise relies heavily on multiple data sources and persistency layers (Data Lake, Historical CSV, SQL Database, Vector Database) to continuously feed the Machine Learning models and RAG pipelines. To ensure the ML models are trained correctly, we need a standalone auditing tool capable of reading all stored data, detecting corruption, analyzing null distributions, and identifying unused storage bloat.

## 1. Auditing Engine (`audit_data.py`)
### Design
- **Standalone Script:** A Python script located at `backend/src/utils/audit_data.py`.
- **Read-Only:** The script will purely extract, read, and aggregate metrics. It will NOT mutate, delete, or clean any database or file. Its purpose is to report the current state.
- **Components:** The tool is logically divided into three analysis blocks.

## 2. Scan Phases
### 2.1 Data Lake (`data/raw/`)
- Traverses all date-partitioned directories.
- Tries to parse each JSON file (`odds_*.json`, `xg_*.json`, `elo_*.json`, `news_*.json`).
- Flags files that are structurally broken (JSONDecodeError), files that are completely empty (0 bytes), or logical blanks (e.g., `{"matches": []}`).
- Computes the total physical size (MB/GB) used by the raw layer to help developers decide on archiving policies.

### 2.2 Historical Cache (`data/historical/merged_history_cache.csv`)
- Loads the primary training dataset using `pandas`.
- Scans for data health critical for Machine Learning:
  - **NaN/Null counts:** Counts how many critical features (`Home_xG`, `Away_xG`, `Home_Elo`, `Away_Elo`) are missing across the entire dataset.
  - **Unrealistic Values:** Flags rows where `Elo` is 0, or `xG` is exactly 0.0 (which might imply broken data for certain matches).
  - **Duplicates:** Detects duplicated match rows (same date, same home and away team).
- Summarizes the shape of the dataset (total matches available for training).

### 2.3 Databases (SQL & Vector)
- **SQLite/PostgreSQL:** Measures the volume of the `teams` table to ensure team aliases are being correctly stored without runaway orphaned records.
- **ChromaDB (`data/chromadb/`):** Connects to the local persistent Chroma client and queries the count of documents in the news collection. Flags if the collection is completely empty or abnormally large.

## 3. Markdown Report Generation
### Design
- The script compiles all findings into a structured, readable Markdown string.
- Automatically saves this output to a new directory: `docs/audits/YYYY-MM-DD-data-health-report.md`.
- The report includes a specific **"Red Alerts"** section highlighting only the critical errors (e.g., "15 JSON files corrupted", "400 matches with missing xG").
- If the script is run in a terminal, it will also print a summary of the alerts directly to stdout.

## Operational Impact
This audit tool is essential to guarantee ML Model reliability by ensuring the models are not being trained on "poisoned" (NaN) or corrupted data. It also serves as a maintenance utility to monitor and manage disk space over time.