"""
Database schema for the NBA chemistry tracker.
Run this file once to create all tables.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    SmallInteger,
    BigInteger,
    String,
    Text,
    Numeric,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

load_dotenv()

Base = declarative_base()


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)  # NBA team ID, e.g. 1610612743
    abbreviation = Column(String(3), nullable=False)
    full_name = Column(Text, nullable=False)


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)  # NBA player ID
    full_name = Column(Text, nullable=False)
    display_name = Column(Text, nullable=False)  # "N. Jokić" — matches API output


class Lineup(Base):
    __tablename__ = "lineups"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    season = Column(String(7), nullable=False)  # "2025-26"
    group_quantity = Column(SmallInteger, nullable=False)  # 2, 3, or 5
    group_id = Column(Text, nullable=False)  # API's lineup identifier
    group_name = Column(Text, nullable=False)  # "N. Jokić - A. Gordon"

    minutes = Column(Numeric(8, 1))
    games_played = Column(SmallInteger)
    net_rating = Column(Numeric(6, 2))
    off_rating = Column(Numeric(6, 2))
    def_rating = Column(Numeric(6, 2))
    pace = Column(Numeric(6, 2))

    fetched_at = Column(DateTime(timezone=True), server_default=func.now())

    players = relationship("LineupPlayer", back_populates="lineup", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("team_id", "season", "group_quantity", "group_id", name="uq_lineup"),
    )


class LineupPlayer(Base):
    __tablename__ = "lineup_players"

    lineup_id = Column(BigInteger, ForeignKey("lineups.id", ondelete="CASCADE"), primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), primary_key=True)

    lineup = relationship("Lineup", back_populates="players")


def init_db():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL not found in .env")

    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    print("Tables created successfully:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")


if __name__ == "__main__":
    init_db()