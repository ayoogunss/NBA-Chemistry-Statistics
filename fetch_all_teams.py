"""
Fetches 2-man lineup data for all 30 NBA teams.
Run after seed_teams.py. Idempotent — safe to re-run.
"""

import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

from schema import Team, Lineup
from fetch_lineups import fetch_team_lineups, SEASON, GROUP_QUANTITY

load_dotenv()

DELAY_BETWEEN_TEAMS = 5  # seconds, to be polite to the NBA API


def team_already_fetched(session, team_id: int) -> bool:
    count = session.scalar(
        select(func.count()).select_from(Lineup).where(
            Lineup.team_id == team_id,
            Lineup.season == SEASON,
            Lineup.group_quantity == GROUP_QUANTITY,
        )
    )
    return count > 0


def fetch_all():
    engine = create_engine(os.getenv("DATABASE_URL"))

    with Session(engine) as session:
        teams = session.execute(select(Team).order_by(Team.full_name)).scalars().all()

    print(f"Found {len(teams)} teams. Starting fetch...\n")

    for i, team in enumerate(teams, start=1):
        print(f"[{i}/{len(teams)}] {team.full_name}")

        with Session(engine) as session:
            if team_already_fetched(session, team.id):
                print(f"  Already fetched — skipping.\n")
                continue

        try:
            fetch_team_lineups(team_id=team.id, team_name=team.full_name)
        except Exception as e:
            print(f"  Unexpected error: {e}")

        if i < len(teams):
            print(f"  Waiting {DELAY_BETWEEN_TEAMS}s before next team...\n")
            time.sleep(DELAY_BETWEEN_TEAMS)

    print("\nDone.")


if __name__ == "__main__":
    fetch_all()