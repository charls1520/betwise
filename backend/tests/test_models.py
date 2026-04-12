from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base
from src.models import Team

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
