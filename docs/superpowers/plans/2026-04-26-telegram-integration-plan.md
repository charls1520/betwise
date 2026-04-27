# Telegram Bot Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate a Telegram Bot to send match predictions one-by-one to a private channel after the daily data ingestion and ML inference processes complete.

**Architecture:** A new dedicated `TelegramNotifier` class in `backend/src/utils/telegram_notifier.py` to format and send predictions to a Telegram channel via the HTTP API, handling rate limits (with exponential backoff and sleep). `backend/src/ingestion/tasks.py` will invoke the ML inference engine and then use the notifier to broadcast the results.

**Tech Stack:** Python 3.11+, `requests` library, Telegram Bot API.

---

### Task 1: Environment Variables Setup

**Files:**
- Modify: `BetWise/.env.example`

- [ ] **Step 1: Add Telegram variables to `.env.example`**

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=-1001234567890
```

- [ ] **Step 2: Commit**

```bash
git add .env.example
git commit -m "chore: add telegram env variables to example config"
```

---

### Task 2: Implement `TelegramNotifier`

**Files:**
- Create: `backend/src/utils/telegram_notifier.py`
- Create: `backend/tests/utils/test_telegram_notifier.py`

- [ ] **Step 1: Write the failing test for `TelegramNotifier` formatting and sending**

Create `backend/tests/utils/test_telegram_notifier.py`:
```python
import pytest
from unittest.mock import patch, MagicMock
from src.utils.telegram_notifier import TelegramNotifier

@patch("src.utils.telegram_notifier.requests.post")
def test_send_prediction(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    notifier = TelegramNotifier(bot_token="test_token", chat_id="test_chat")
    prediction = {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "commence_time": "2026-04-26T15:00:00Z",
        "prob_home_win": 0.45,
        "prob_draw": 0.25,
        "prob_away_win": 0.30,
        "prob_over25": 0.55,
        "prob_under25": 0.45,
        "implied_home_prob": 0.40,
        "implied_away_prob": 0.35,
        "implied_draw_prob": 0.25,
        "home_odds": 2.50,
        "away_odds": 2.85,
        "draw_odds": 4.00,
        "value_edge": True
    }

    result = notifier.send_prediction(prediction)
    
    assert result is True
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "api.telegram.org/bottest_token/sendMessage" in args[0]
    assert kwargs["json"]["chat_id"] == "test_chat"
    assert "Arsenal vs Chelsea" in kwargs["json"]["text"]
    assert "🟢" in kwargs["json"]["text"] # Value edge indicator
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/utils/test_telegram_notifier.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.utils.telegram_notifier'"

- [ ] **Step 3: Write minimal implementation**

Create `backend/src/utils/telegram_notifier.py`:
```python
import os
import time
import requests
from src.utils.logger import get_logger

logger = get_logger()

class TelegramNotifier:
    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def format_message(self, pred: dict) -> str:
        home = pred.get("home_team", "Unknown")
        away = pred.get("away_team", "Unknown")
        date = pred.get("commence_time", "Unknown Date")
        
        prob_h = pred.get("prob_home_win", 0) * 100
        prob_d = pred.get("prob_draw", 0) * 100
        prob_a = pred.get("prob_away_win", 0) * 100
        prob_o = pred.get("prob_over25", 0) * 100
        prob_u = pred.get("prob_under25", 0) * 100
        
        odds_h = pred.get("home_odds", 0.0)
        odds_d = pred.get("draw_odds", 0.0)
        odds_a = pred.get("away_odds", 0.0)

        value_edge = pred.get("value_edge", False)
        value_icon = " 🟢 *VALUE EDGE DETECTED*" if value_edge else ""

        msg = f"🏆 *{home} vs {away}*\n"
        msg += f"📅 {date}\n\n"
        msg += f"📊 *1X2 Prediction:*\n"
        msg += f"• Home: {prob_h:.1f}% (Odds: {odds_h})\n"
        msg += f"• Draw: {prob_d:.1f}% (Odds: {odds_d})\n"
        msg += f"• Away: {prob_a:.1f}% (Odds: {odds_a})\n\n"
        msg += f"⚽ *Goals Prediction:*\n"
        msg += f"• Over 2.5: {prob_o:.1f}%\n"
        msg += f"• Under 2.5: {prob_u:.1f}%\n"
        msg += value_icon
        
        return msg

    def send_prediction(self, pred: dict, max_retries: int = 3) -> bool:
        if not self.bot_token or not self.chat_id:
            logger.error("Telegram credentials missing.")
            return False

        text = self.format_message(pred)
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, json=payload, timeout=10)
                if response.status_code == 200:
                    time.sleep(1.5)  # Rate limiting
                    return True
                elif response.status_code == 429:
                    retry_after = response.json().get("parameters", {}).get("retry_after", 5)
                    logger.warning(f"Rate limited by Telegram. Retrying in {retry_after}s...")
                    time.sleep(retry_after)
                else:
                    logger.error(f"Telegram API error {response.status_code}: {response.text}")
                    break
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error sending to Telegram: {e}")
                time.sleep(2 ** attempt)

        return False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/utils/test_telegram_notifier.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/utils/telegram_notifier.py backend/tests/utils/test_telegram_notifier.py
git commit -m "feat: implement telegram notifier for predictions"
```

---

### Task 3: Integrate Notifier in Ingestion Tasks

**Files:**
- Modify: `backend/src/ingestion/tasks.py`
- Modify: `backend/tests/ingestion/test_tasks.py`

- [ ] **Step 1: Write the failing test for integration**

Modify `backend/tests/ingestion/test_tasks.py`. Add this test at the end:
```python
@patch("src.ingestion.tasks.TelegramNotifier")
@patch("src.ingestion.tasks.predict_matches")
@patch("src.ingestion.tasks.save_raw_data")
@patch("src.ingestion.tasks.fetch_current_xg_stats")
@patch("src.ingestion.tasks.fetch_premier_league_odds")
@patch("src.ingestion.tasks.fetch_clubelo_stats")
@patch("src.ingestion.tasks.fetch_bbc_sports_news")
def test_run_daily_scraping_with_telegram(
    mock_fetch_news,
    mock_fetch_elo,
    mock_fetch_odds,
    mock_fetch_xg,
    mock_save,
    mock_predict,
    mock_notifier
):
    mock_fetch_news.return_value = [{"title": "News", "url": "http://bbc.com/1", "published_date": "2026-04-20T10:00:00Z", "summary": "Summary"}]
    mock_fetch_elo.return_value = [{"team": "Arsenal", "elo": 1900}]
    mock_fetch_odds.return_value = [{"home_team": "Arsenal", "away_team": "Chelsea", "commence_time": "2026-04-26T15:00:00Z", "bookmakers": []}]
    mock_fetch_xg.return_value = {"Arsenal": {"xG": 2.0}, "Chelsea": {"xG": 1.5}}
    
    mock_predict.return_value = [
        {"home_team": "Arsenal", "away_team": "Chelsea", "value_edge": True, "prob_home_win": 0.6}
    ]
    
    mock_notifier_instance = mock_notifier.return_value
    
    from src.ingestion.tasks import run_daily_scraping
    run_daily_scraping(odds_api_key="test_key")
    
    mock_predict.assert_called_once()
    mock_notifier_instance.send_prediction.assert_called_once_with(
        {"home_team": "Arsenal", "away_team": "Chelsea", "value_edge": True, "prob_home_win": 0.6}
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/ingestion/test_tasks.py::test_run_daily_scraping_with_telegram -v`
Expected: FAIL because `TelegramNotifier` and `predict_matches` are not used in `run_daily_scraping`.

- [ ] **Step 3: Write minimal implementation**

Modify `backend/src/ingestion/tasks.py`:
Add imports at the top:
```python
from src.ml.inference import predict_matches
from src.utils.telegram_notifier import TelegramNotifier
```

At the end of `run_daily_scraping`, after `if len(all_xg) > 0:` block, add:
```python
    logger.info("Running ML inference on new odds...")
    if len(all_odds) > 0:
        try:
            predictions = predict_matches(all_odds)
            logger.info(f"Generated predictions for {len(predictions)} matches. Notifying Telegram...")
            
            notifier = TelegramNotifier()
            for pred in predictions:
                notifier.send_prediction(pred)
                
            logger.info("Telegram notifications sent.")
        except Exception as e:
            logger.error(f"Failed to run inference or send notifications: {e}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/ingestion/test_tasks.py::test_run_daily_scraping_with_telegram -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/ingestion/tasks.py backend/tests/ingestion/test_tasks.py
git commit -m "feat: integrate telegram notifier in daily scraping task"
```

---

### Task 4: Update Master Plan

**Files:**
- Modify: `docs/MASTER-PLAN.md`

- [ ] **Step 1: Update Master Plan**
Add a new sub-project or step reflecting the Telegram Integration.

- [ ] **Step 2: Commit**
```bash
git add docs/MASTER-PLAN.md
git commit -m "docs: update master plan with telegram integration"
```
