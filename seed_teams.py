"""
One-time seed: populates the teams table with all 30 NBA teams.
Safe to re-run — uses upsert logic.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from nba_api.stats.static import teams as nba_teams

from schema import Team

load_dotenv()


def seed_teams():
    engine = create_engine(os.getenv("DATABASE_URL"))

    all_teams = nba_teams.get_teams()
    print(f"Fetched {len(all_teams)} teams from nba_api")

    with Session(engine) as session:
        for t in all_teams:
            stmt = insert(Team).values(
                id=t["id"],
                abbreviation=t["abbreviation"],
                full_name=t["full_name"],
            )
            # If team already exists, just update the names (no-op the first time)
            stmt = stmt.on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "abbreviation": stmt.excluded.abbreviation,
                    "full_name": stmt.excluded.full_name,
                },
            )
            session.execute(stmt)
        session.commit()

    print("Teams seeded.")


if __name__ == "__main__":
    seed_teams()