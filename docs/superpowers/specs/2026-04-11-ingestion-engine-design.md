# BetWise Ingestion and Normalization Engine Design

## 1. Overview and Purpose
This spec covers the **Data Ingestion and Normalization Engine** for BetWise.
The goal is to reliably extract three distinct types of data (Historical Stats, Betting Odds, and Unstructured News) from external sources, standardize them, and load them into our operational databases without risking data corruption if a scraper fails mid-run.

## 2. Architecture: Two-Stage Data Pipeline
We will use a **Data Lake -> ETL** (Extract, Transform, Load) architecture to ensure resilience.

### Stage 1: Extraction (Raw Data Lake)
* **Scrapers (Python/BeautifulSoup/Playwright):** Separate scraper modules for Stats, Odds, and News.
* **Storage:** Extracted data is immediately saved as raw `.json` or `.csv` files in a local directory (e.g., `data/raw/YYYY-MM-DD/`).
* **Benefit:** If normalization fails or the database schema changes, we still have the raw data and don't need to re-scrape (saving API calls and avoiding IP bans).

### Stage 2: Transform and Load (ETL & Normalization)
* **Normalization Engine:** Reads the raw files. This is where the **Fuzzy Name Matching** (e.g., matching "Man Utd" to "Manchester United") happens before any database insertion.
* **Relational Load:** Cleaned stats and odds are inserted into SQLite/PostgreSQL.
* **Vector Load (RAG):** Cleaned news articles are chunked, passed through an embedding model, and loaded into ChromaDB (or similar) via LlamaIndex.

## 3. Data Sources (Targeted)
1.  **Historical Stats & Results:** E.g., FBref or Understat (for xG, shots, corners, cards).
2.  **Betting Odds:** E.g., OddsPortal or a free odds API (for 1X2, Asian Lines, Over/Under).
3.  **News & Injuries:** E.g., BBC Sport or team-specific RSS feeds.

## 4. Normalization Strategy
*   **The Problem:** "Arsenal FC" (Stats) vs "Arsenal" (Odds) vs "The Gunners" (News).
*   **The Solution:** A `TeamAlias` mapping table in the relational database. When the ETL script encounters an unknown team name, it uses a string similarity library (`thefuzz`) to suggest the closest canonical name. If the confidence is high (>90%), it maps automatically; if low, it logs it for manual review.

## 5. Execution and Scheduling
*   The system will be triggered by a Cron Job or a simple task scheduler (like `APScheduler` or Celery) running within the FastAPI backend context.
*   **Daily Run:** e.g., 03:00 AM for Stats/Odds, and potentially more frequently for News (e.g., every 6 hours).