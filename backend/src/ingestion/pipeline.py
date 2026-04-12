import json
from sqlalchemy.orm import Session
from src.models import Team
from src.ingestion.normalizer import TeamNormalizer


def run_etl_pipeline(db: Session, raw_filepath: str) -> dict:
    with open(raw_filepath, "r") as f:
        raw_data = json.load(f)

    # Get canonical teams from DB
    teams = db.query(Team).all()
    canonical_names = [t.canonical_name for t in teams if t.canonical_name]

    normalizer = TeamNormalizer(canonical_names)
    normalized_matches = []

    for match in raw_data.get("matches", []):
        home_raw = match.get("home")
        home_canonical = normalizer.normalize(home_raw) if home_raw else None

        normalized_matches.append(
            {
                "original_home": home_raw,
                "home_canonical": home_canonical,
                "home_goals": match.get("home_goals"),
            }
        )

    return {"normalized_matches": normalized_matches}
