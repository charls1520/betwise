# System Health & Audit Panel Design

## 1. Overview
This specification details the implementation of a **System Health & Audit Panel** for the BetWise Frontend, integrated as part of the "Testing & Bugfixing" phase.
The primary goal is to provide absolute transparency to the user regarding the data feeding the ML and RAG engines, proving that predictions are based on real, auditable data rather than mock values or hallucinations.

## 2. Backend Enhancements (Audit API)
We will introduce a new endpoint `/api/health/audit` that gathers metadata about the ingestion, ML, and RAG pipelines.

### 2.1 Audit Data Points
The API will return a JSON payload containing:
*   **RAG Engine Status:**
    *   `last_news_indexed`: Title and timestamp of the most recent article loaded into ChromaDB.
    *   `total_documents`: Number of news chunks currently active in the vector store.
*   **ML Engine Status:**
    *   `model_last_trained`: Timestamp of the `.joblib` model file creation.
    *   `training_dataset_size`: Number of historical matches (e.g., 1900) used to train the current model.
    *   `sources_used`: E.g., `["football-data.co.uk (E0.csv)"]`.
*   **Ingestion Engine Status:**
    *   `last_odds_fetch`: Timestamp of the last successful call to The-Odds-API.
    *   `last_xg_fetch`: Timestamp of the last successful Playwright scrape of Understat.
    *   `normalization_warnings`: A list of teams that failed the strict 95% `thefuzz` threshold during the last ETL run (e.g., `["Leeds United", "Luton Town"]`).

## 3. Frontend Integration (React/Tailwind)
*   **Placement:** The audit information will be accessible via a subtle "System Health" or "Audit Log" button in the Top Navigation Bar (e.g., replacing or next to the `analytics` icon in the Kinetic Vault header).
*   **UI Component:** A sleek, dark-themed Modal or Slide-over panel.
*   **Design Language:** Matches the "Kinetic Vault" aesthetic (Deep Navy backgrounds, Neon Green text for healthy status, Red/Orange for warnings like unmapped teams or stale models).
*   **Interactivity:** The panel will fetch data from `/api/health/audit` when opened, ensuring the user always sees the live state of the backend engines.