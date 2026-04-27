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
