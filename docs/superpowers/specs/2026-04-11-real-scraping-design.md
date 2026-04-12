# Real Data Scraping Implementation Design

## 1. Overview
This specification details the implementation of real data scrapers for the BetWise Ingestion Engine.
The objective is to replace the dummy data generators with actual scraping/API scripts for three core domains: Historical Stats, Betting Odds, and Unstructured News.

## 2. Scraping Strategies by Domain

### 2.1 Historical Stats & Results (Target: FBref or Understat)
*   **Approach:** HTML Scraping via `BeautifulSoup` and `requests`.
*   **Data Points:** Expected Goals (xG), Possession, Shots on Target, Cards, Corners.
*   **Challenges:** Rate limiting.
*   **Solution:** Introduce `time.sleep()` between requests (e.g., 3-5 seconds) and use rotating User-Agents. We will focus only on the current Premier League season to limit the request volume.

### 2.2 Betting Odds (Target: The-Odds-API / Free Tier)
*   **Approach:** REST API consumption.
*   **Data Points:** Match-winner (1X2), Over/Under 2.5, Asian Handicap.
*   **Why API over Scraping:** Odds sites are heavily obfuscated and employ strict anti-bot measures (Cloudflare, reCAPTCHA). Using a free tier API (like `the-odds-api.com`) is significantly more reliable for the initial version. If rate limits are hit, we will mock the fallback, but the primary pipeline will expect real API JSON structures.

### 2.3 News & Unstructured Text for RAG (Target: BBC Sport RSS / Team Feeds)
*   **Approach:** RSS Feed parsing using `feedparser` combined with `BeautifulSoup` for article extraction.
*   **Data Points:** Article Title, Published Date, Full Text Content.
*   **Pipeline Integration:** Scraped articles will be saved to the Data Lake (`.json`) and subsequently processed by LlamaIndex to be embedded and stored in ChromaDB during the ETL phase.

## 3. Resilience and Rate Limiting
*   All scrapers will implement standard retry logic (`tenacity` library) for transient network failures (e.g., 502/503 errors).
*   Data will be aggressively cached locally in the Data Lake using the `save_raw_data` function built previously. If an ETL step fails, we do not re-scrape.

## 4. Normalization Engine Update
*   The `TeamNormalizer` (using `thefuzz`) built in the previous phase will be actively used. As we introduce real data from 3 different sources, the manual override list in `normalizer.py` will likely need expansion to handle discrepancies like "Man Utd" (News) vs "Manchester United" (Odds).