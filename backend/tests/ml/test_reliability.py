from src.ml.reliability import calculate_value_edge, meets_data_threshold


def test_value_edge():
    # Model says 65% (0.65) probability of home win.
    # Bookie pays 2.00 (implied probability 50% or 0.50).
    # Edge is 0.65 - 0.50 = 0.15 (15% edge).
    assert calculate_value_edge(model_prob=0.65, bookie_decimal_odds=2.0) == 0.15

    # Negative edge
    assert calculate_value_edge(model_prob=0.40, bookie_decimal_odds=2.0) == -0.10


def test_data_threshold():
    # In V1 we mock the 10 match threshold check by looking if the team exists in the xG stats
    stats = {"Arsenal": {"xg_for_avg": 2.1, "matches_played": 15}}
    assert meets_data_threshold("Arsenal", stats) is True

    stats_low = {"Ipswich": {"xg_for_avg": 1.1, "matches_played": 5}}
    assert meets_data_threshold("Ipswich", stats_low) is False

    assert meets_data_threshold("Unknown Team", stats) is False
