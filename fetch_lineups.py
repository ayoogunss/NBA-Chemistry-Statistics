"""
Fetches 2-man lineup data for a single team and writes it to the database.
Once verified working for one team, we'll loop over all 30.
"""

import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from nba_api.stats.endpoints import teamdashlineups
from nba_api.stats.static import players as nba_players

from schema import Player, Lineup, LineupPlayer

load_dotenv()

SEASON = "2025-26"
GROUP_QUANTITY = 2


def parse_player_ids(group_id: str) -> list[int]:
    """GROUP_ID looks like '-201939-203954-'. Strip the leading/trailing dashes and split."""
    return [int(pid) for pid in group_id.strip("-").split("-")]


def derive_display_name(full_name: str) -> str:
    """'Nikola Jokić' -> 'N. Jokić'. Best-effort; will be slightly off for Jr/Sr/III players."""
    parts = full_name.split(" ", 1)
    if len(parts) < 2:
        return full_name
    return f"{parts[0][0]}. {parts[1]}"


def upsert_player(session, player_id: int):
    """Ensures the player exists in the players table.
    Falls back to API call if not in the static player list."""
    existing = session.get(Player, player_id)
    if existing:
        return

    info = nba_players.find_player_by_id(player_id)

    if not info:
        # Static list missed it (probably a rookie). Fetch from API.
        from nba_api.stats.endpoints import commonplayerinfo
        try:
            time.sleep(0.6)  # be polite to the API
            resp = commonplayerinfo.CommonPlayerInfo(player_id=player_id, timeout=30)
            row = resp.get_data_frames()[0].iloc[0]
            full_name = f"{row['FIRST_NAME']} {row['LAST_NAME']}"
        except Exception as e:
            print(f"  Warning: failed to fetch player {player_id} from API: {e}")
            return
    else:
        full_name = info["full_name"]

    session.execute(
        insert(Player).values(
            id=player_id,
            full_name=full_name,
            display_name=derive_display_name(full_name),
        ).on_conflict_do_nothing(index_elements=["id"])
    )


def fetch_team_lineups(team_id: int, team_name: str, max_retries: int = 3):
    engine = create_engine(os.getenv("DATABASE_URL"))

    print(f"Fetching {team_name} ({team_id}) — {SEASON}, {GROUP_QUANTITY}-man lineups...")

    df = None
    for attempt in range(1, max_retries + 1):
        try:
            response = teamdashlineups.TeamDashLineups(
                team_id=team_id,
                season=SEASON,
                group_quantity=GROUP_QUANTITY,
                measure_type_detailed_defense="Advanced",
                per_mode_detailed="Per100Possessions",
                timeout=90,
            )
            df = response.get_data_frames()[1]
            if len(df) == 0:
                raise ValueError("Empty data frame returned")
            break
        except Exception as e:
            print(f"  Attempt {attempt}/{max_retries} failed: {type(e).__name__}: {e}")
            if attempt < max_retries:
                wait = 10 * attempt  # 10s, 20s, 30s
                print(f"  Waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                print(f"  Giving up on {team_name}.")
                return

    print(f"  Got {len(df)} lineups from API")

    with Session(engine) as session:
        for _, row in df.iterrows():
            player_ids = parse_player_ids(row["GROUP_ID"])

            for pid in player_ids:
                upsert_player(session, pid)

            stmt = insert(Lineup).values(
                team_id=team_id,
                season=SEASON,
                group_quantity=GROUP_QUANTITY,
                group_id=row["GROUP_ID"],
                group_name=row["GROUP_NAME"],
                minutes=row["MIN"],
                games_played=row["GP"],
                net_rating=row["NET_RATING"],
                off_rating=row["OFF_RATING"],
                def_rating=row["DEF_RATING"],
                pace=row["PACE"],
            ).on_conflict_do_update(
                index_elements=["team_id", "season", "group_quantity", "group_id"],
                set_={
                    "minutes": row["MIN"],
                    "games_played": row["GP"],
                    "net_rating": row["NET_RATING"],
                    "off_rating": row["OFF_RATING"],
                    "def_rating": row["DEF_RATING"],
                    "pace": row["PACE"],
                },
            ).returning(Lineup.id)

            lineup_id = session.execute(stmt).scalar()

            for pid in player_ids:
                session.execute(
                    insert(LineupPlayer).values(
                        lineup_id=lineup_id, player_id=pid
                    ).on_conflict_do_nothing()
                )

        session.commit()

    print(f"  Wrote {len(df)} lineups to database.")


if __name__ == "__main__":
    # Denver Nuggets — same team we explored in the notebook
    fetch_team_lineups(team_id=1610612743, team_name="Denver Nuggets")