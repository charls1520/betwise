import os
from dotenv import load_dotenv
from src.utils.telegram_notifier import TelegramNotifier

load_dotenv()

def run_test():
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or bot_token == "your_bot_token_here":
        print("Error: TELEGRAM_BOT_TOKEN is missing or not configured correctly.")
        return
        
    if not chat_id or chat_id == "-1001234567890":
        print("Error: TELEGRAM_CHAT_ID is missing or not configured correctly.")
        return
        
    print(f"Testing Telegram Notifier with Chat ID: {chat_id}")
    
    notifier = TelegramNotifier()
    
    dummy_pred = {
        "home_team": "Manchester City",
        "away_team": "Real Madrid",
        "commence_time": "2026-05-10T19:00:00Z",
        "prob_home_win": 0.55,
        "prob_draw": 0.25,
        "prob_away_win": 0.20,
        "prob_over25": 0.65,
        "prob_under25": 0.35,
        "implied_home_prob": 0.40,
        "implied_away_prob": 0.35,
        "implied_draw_prob": 0.25,
        "home_odds": 2.50,
        "draw_odds": 4.00,
        "away_odds": 2.85,
        "value_edge": True
    }
    
    success = notifier.send_prediction(dummy_pred)
    
    if success:
        print("[SUCCESS] Message sent successfully to Telegram!")
    else:
        print("[FAILED] Failed to send message to Telegram. Check your logs.")

if __name__ == "__main__":
    run_test()
