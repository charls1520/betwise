def calculate_value_edge(model_prob: float, bookie_decimal_odds: float) -> float:
    """
    Calculates the mathematical edge of a bet.
    Edge = Model Probability - Implied Bookmaker Probability
    """
    if bookie_decimal_odds <= 0:
        return 0.0

    implied_prob = 1.0 / bookie_decimal_odds
    return round(model_prob - implied_prob, 4)


def meets_data_threshold(team_name: str, xg_stats: dict, min_matches: int = 10) -> bool:
    """
    Checks if a team has enough historical data to make a reliable prediction.
    """
    if not xg_stats or team_name not in xg_stats:
        return False

    team_data = xg_stats[team_name]
    # Since our scraper currently only grabs averages, we will mock the matches_played
    # check for now by assuming if they have data in the dict, they passed the threshold,
    # unless matches_played is explicitly provided and too low.
    if "matches_played" in team_data:
        return team_data["matches_played"] >= min_matches

    # If no matches_played field, assume true if data exists
    return True
