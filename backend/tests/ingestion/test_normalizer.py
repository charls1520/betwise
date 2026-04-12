from src.ingestion.normalizer import TeamNormalizer


def test_strict_normalize_team_name():
    canonical_teams = ["Manchester United", "Arsenal", "Chelsea"]
    normalizer = TeamNormalizer(canonical_teams, threshold=95)

    assert normalizer.normalize("Man Utd") == "Manchester United"  # via manual override
    assert (
        normalizer.normalize("Arsenal Football Club") is None
    )  # Fails 95% threshold without override
