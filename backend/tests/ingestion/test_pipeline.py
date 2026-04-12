from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base
from src.models import Team
from src.ingestion.pipeline import run_etl_pipeline
import os
import json

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_pipeline.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def test_run_etl_pipeline(tmp_path):
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Pre-seed canonical team
    db.add(Team(name="Arsenal FC", canonical_name="Arsenal"))
    db.commit()

    # Create fake raw data
    raw_data = {"matches": [{"home": "Arsenal FC", "away": "Chelsea", "home_goals": 2}]}
    filepath = os.path.join(tmp_path, "fake_stats.json")
    with open(filepath, "w") as f:
        json.dump(raw_data, f)

    # Run pipeline
    results = run_etl_pipeline(db, filepath)

    assert len(results["normalized_matches"]) == 1
    assert results["normalized_matches"][0]["home_canonical"] == "Arsenal"

    db.close()
    Base.metadata.drop_all(bind=engine)
