# Machine Learning Engine Design

## 1. Overview
This specification details the architecture for the **Machine Learning Engine** of BetWise.
The goal is to calculate fair probabilities for upcoming Premier League matches across three distinct markets: Match Winner (1X2), Total Goals (Over/Under 2.5), and Secondary Markets (Corners/Cards), and compare them against scraped bookmaker odds to find "Value Bets".

## 2. Architecture: Independent Models
We will use an **Independent Model per Market** approach. This allows us to select the best algorithm for the specific nature of each market, makes debugging easier, and prevents poor performance in one market from affecting the others.

### 2.1 Match Winner (1X2)
*   **Algorithm:** `XGBoost` or `RandomForestClassifier` (via `scikit-learn` / `xgboost`).
*   **Features (Inputs):** Team Elo ratings, Recent form (last 5 games points), Head-to-Head history, Home Advantage modifier, Expected Goals (xG) difference over the season.
*   **Output:** Probabilities for Home Win, Draw, Away Win (summing to 100%).

### 2.2 Total Goals (Over/Under 2.5)
*   **Algorithm:** Poisson Regression (Statistical) or `LogisticRegression`.
*   **Features (Inputs):** Home Team Average xG Scored (Home), Home Team Average xG Conceded (Home), Away Team Average xG Scored (Away), Away Team Average xG Conceded (Away).
*   **Output:** Probability of Under 2.5 goals and Over 2.5 goals.

### 2.3 Secondary Markets (Corners & Cards)
*   **Algorithm:** Ridge Regression (Linear model with regularization) or simple Poisson distribution based on rolling averages.
*   **Features (Inputs):** Rolling average of corners/cards won and conceded, Referee strictness index (for cards), Team playstyle metrics (e.g., cross frequency for corners).
*   **Output:** Expected number of corners/cards, converted into probabilities for Over/Under lines (e.g., Over 9.5 Corners).

## 3. Training and Inference Pipeline
1.  **Data Preparation (Feature Engineering):** A module that reads historical match data from our SQLite database (populated by the ETL pipeline) and calculates rolling averages, forms, and target variables.
2.  **Training Script:** A standalone script run periodically (e.g., weekly) to retrain the models with the latest results. Trained models are serialized and saved to disk (e.g., using `joblib` or `pickle` in `backend/models/`).
3.  **Inference (Daily Cron):** After the daily Odds and Stats scraping completes, an Inference module loads the saved models, calculates the probabilities for upcoming matches, compares them with the scraped odds, and flags matches where our model's probability is significantly higher than the bookmaker's implied probability (Value Bets).

## 4. Tech Stack Requirements
*   `scikit-learn`
*   `pandas` (for feature engineering and data manipulation)
*   `numpy`
*   `xgboost` (optional, if we use it for 1X2)