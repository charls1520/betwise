from src.ingestion.normalizer import TeamNormalizer


def test_normalize_team_name():
    canonical_teams = ["Manchester United", "Arsenal", "Chelsea"]
    normalizer = TeamNormalizer(canonical_teams)

    assert normalizer.normalize("Man Utd") == "Manchester United"
    assert normalizer.normalize("Arsenal FC") == "Arsenal"
    assert normalizer.normalize("The Blues") is None  # Below confidence threshold
