from sqlalchemy import Column, Integer, String, Float, ForeignKey
from src.database import Base


class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    canonical_name = Column(String, index=True)


class League(Base):
    __tablename__ = "leagues"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)


class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)


class TeamStats(Base):
    __tablename__ = "team_stats"
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    match_id = Column(Integer, ForeignKey("matches.id"))
    possession_percentage = Column(Float, nullable=True)


class Derby(Base):
    __tablename__ = "derbies"
    id = Column(Integer, primary_key=True)
    team1_id = Column(Integer, ForeignKey("teams.id"))
    team2_id = Column(Integer, ForeignKey("teams.id"))
    league_id = Column(Integer, ForeignKey("leagues.id"))
    derby_name = Column(String)


class MatchAbsence(Base):
    __tablename__ = "match_absences"
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    player_name = Column(String)
    reason = Column(String)