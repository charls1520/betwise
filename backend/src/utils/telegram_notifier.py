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
