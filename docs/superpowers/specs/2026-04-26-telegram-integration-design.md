# Design Spec: Telegram Bot Integration

## 1. Overview
Integrate a Telegram Bot to send match predictions one-by-one to a private channel after the daily data ingestion and ML inference processes complete.

## 2. Architecture & Communication
- **Component**: A new dedicated `TelegramNotifier` class in `backend/src/utils/telegram_notifier.py`.
- **Execution Flow**:
  1. Data ingestion completes (`run_daily_scraping` in `tasks.py`).
  2. The system invokes the ML inference engine (`predict_matches`) to calculate probabilities (1X2, Over/Under) and identify value edges.
  3. The `TelegramNotifier` formats these predictions and sends them sequentially to the configured Telegram channel using standard HTTP requests (`requests` library).
- **Configuration**: `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` will be added to `.env`.

## 3. Message Format & Content
- **Scope**: ALL processed matches will be sent to the channel, regardless of whether they have a value edge.
- **Format**: Clean Telegram Markdown/HTML template containing:
  - 🏆 **Match Details**: Home vs Away, Date/Time.
  - 📊 **1X2 Prediction**: ML-calculated probabilities vs. actual bookmaker odds.
  - ⚽ **Goals Prediction**: Over/Under 2.5 probabilities.
  - 🟢 **Value Edge Highlight**: A visual indicator if the model detects a value edge (real probability > implied odds), ensuring valuable opportunities stand out even when all matches are sent.

## 4. Rate Limits & Reliability
- **Throttling**: To avoid hitting Telegram's anti-spam limits (e.g., max 20 messages per minute), a `time.sleep(1.5)` will be implemented between consecutive message sends.
- **Resilience**: The notifier will handle `HTTP 429 (Too Many Requests)` errors and network timeouts by implementing an exponential backoff retry mechanism to ensure no matches are skipped.
