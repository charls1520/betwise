from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base
from src.models import Team, Derby, MatchAbsence, TeamStats

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_create_team():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    new_team = Team(name="Arsenal FC", canonical_name="Arsenal")
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    assert new_team.id is not None
    assert new_team.canonical_name == "Arsenal"
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_derby_model_creation():
    derby = Derby(team1_id=1, team2_id=2, league_id=1, derby_name="El Clásico")
    assert derby.derby_name == "El Clásico"

def test_match_absence_creation():
    absence = MatchAbsence(match_id=1, team_id=1, player_name="Messi", reason="Injured")
    assert absence.player_name == "Messi"

def test_team_stats_possession_column():
    stats = TeamStats(team_id=1, match_id=1, possession_percentage=55.5)
    assert stats.possession_percentage == 55.5