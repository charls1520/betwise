# Real ML Engine & Scraping Integration Spec (v3)

## 1. Overview
This specification details the transition from mock/dummy data to a fully verifiable, real-data pipeline for the BetWise Machine Learning Engine.
The goal is to eliminate all hardcoded variables and rely strictly on audited, real-world data sources for both model training and daily inference.

## 2. Data Sources & Audibility
To guarantee data reliability, we will strictly use established platforms. The ingestion engine will scrape/fetch data, normalize it, and store it raw in the Data Lake for auditability.

### 2.1 Historical Training Data (The Baseline)
*   **Source:** Understat (via web scraping or Python libraries like `understat`) for comprehensive Expected Goals (xG), shot data, and historical match results for the Premier League (last 3-5 seasons).
*   **Alternative/Complementary Source:** Football-Data.co.uk (CSV downloads) for historical closing odds, cards, and referee data.
*   **Auditability:** Raw historical data files will be permanently stored in `data/historical/` and version-controlled or backed up.

### 2.2 Live Inference Data (The Daily Pulse)
*   **Understat:** Scraped daily for the latest team xG rolling averages and recent form.
*   **The-Odds-API:** Queried for live bookmaker odds (1X2, Over/Under).
*   **BeSoccer / Flashscore (Optional/Fallback):** Scraped via Playwright/BeautifulSoup for specific secondary market data (lineups, corner stats) if Understat lacks them.
*   **BBC Sport RSS:** Parsed for unstructured text (injuries, press conferences) to feed the RAG engine.

## 3. Strict Normalization Engine
*   The `TeamNormalizer` module will be upgraded to be virtually foolproof.
*   **Mapping Table:** A hardcoded, exhaustive JSON or DB table mapping known aliases from specific sources to our canonical IDs.
    *   *Example:* Understat ("Manchester United"), The-Odds-API ("Manchester United"), Flashscore ("Man Utd"), BeSoccer ("Man. United") -> Canonical ID `MUN`.
*   **Fuzzy Fallback:** `thefuzz` will only be used as a fallback. If a fuzzy match confidence is below 95%, the system will halt processing for that match and log an "Unmapped Team Exception" requiring manual developer intervention, preventing poisoned data from entering the ML model.

## 4. ML Pipeline Execution
1.  **ETL Script:** Reads raw JSONs from the Data Lake, applies strict normalization, and inserts rows into the SQLite database.
2.  **Feature Engineering:** Reads from SQLite and calculates rolling averages (e.g., "Last 5 matches xG For", "Home xG Conceded"). **No dummy data (like static 1.5 xG) is allowed.**
3.  **Training:** The `RandomForest` (1X2) and `LogisticRegression` (Goals) models are trained exclusively on the structured historical data.
4.  **Inference:** The models predict probabilities for upcoming matches using the live Understat rolling averages and compare them against live Odds API data to find the "Edge".

## 5. Technology Additions
*   `playwright` or `selenium` (if rendering JavaScript is required for Flashscore/BeSoccer).
*   `understat` (Python wrapper, if available and reliable, otherwise manual `BeautifulSoup`).