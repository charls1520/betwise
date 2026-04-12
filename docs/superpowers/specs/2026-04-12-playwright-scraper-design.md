# Playwright Scraper Engine Design

## 1. Overview
This specification details the transition from simple HTTP requests (`requests`/`BeautifulSoup`) to a robust Headless Browser scraping architecture using **Playwright** for the BetWise Ingestion Engine.
The primary goal is to bypass anti-bot protections (like Cloudflare) employed by modern sports statistics websites (Understat, Sofascore, Flashscore) to ensure 100% real, auditable data extraction without relying on hardcoded mocks or fallbacks.

## 2. Architecture & Approach
We will replace the fragile `requests`-based scrapers with Playwright scripts that render the full DOM and execute JavaScript.

### 2.1 Headless Browser Engine
*   **Tool:** `playwright` (Python asynchronous API).
*   **Execution:** The scraper will launch a Chromium instance in headless mode, navigate to the target URLs, wait for the necessary data elements or JSON payloads to load in the DOM/Network tab, and extract them.
*   **Benefits:** Can execute complex JavaScript, bypass basic bot checks by mimicking real user behavior (setting user agents, viewports, and handling cookies), and wait for dynamic content (like React/Vue apps on Sofascore) to render.

### 2.2 Target Sources & Data Extraction
*   **Understat (xG & Advanced Stats):**
    *   Navigate to the league page.
    *   Extract the `teamsData` JSON directly from the evaluated JavaScript context or DOM elements after the page fully loads.
*   **Flashscore / Sofascore (Lineups, Live Data, Corners/Cards):**
    *   Navigate to specific match pages.
    *   Wait for the statistics tabs/containers to become visible.
    *   Extract specific metrics (Corners, Yellow/Red Cards, Ball Possession, Shots on Target).

### 2.3 Strict Data Pipeline Integration
*   The Playwright scrapers will be integrated into the existing `tasks.py` orchestrator.
*   **No Mocks Policy:** The fallback mechanisms that returned dummy data (e.g., static xG of 1.5 or the hardcoded "Arsenal vs Chelsea" match) will be completely removed. If a scraper fails after all retries, the pipeline will log a critical error and halt the specific update, ensuring the ML engine only trains and infers on verified data.
*   **Normalization:** The strict 95% threshold `TeamNormalizer` remains in place to unify the names scraped from these visually distinct platforms.

## 3. Resilience and Resource Management
*   **Timeouts & Retries:** Playwright scripts will include explicit network idle waits and DOM element visibility checks. `tenacity` will still be used for high-level retries.
*   **Resource Footprint:** Playwright browsers will be instantiated and closed cleanly using context managers (`async with`) to prevent memory leaks in the FastAPI backend environment.

## 4. Tech Stack Requirements
*   `playwright`
*   `nest-asyncio` (to allow running Playwright's async event loop within the existing synchronous or FastAPI async contexts).