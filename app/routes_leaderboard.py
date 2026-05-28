"""
League-wide leaderboard endpoints — best and worst lineups across all teams.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, asc

from schema import Lineup, Team
from app.database import get_session

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("/")
def leaderboard(
    season: str = Query("2025-26"),
    group_quantity: int = Query(2, ge=2, le=5),
    min_minutes: float = Query(500.0, ge=0, description="Higher defaults for league-wide ranking"),
    sort_by: str = Query("net_rating", regex="^(net_rating|off_rating|def_rating|minutes)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    limit: int = Query(25, ge=1, le=100),
    session: Session = Depends(get_session),
):
    """Top (or bottom) lineups league-wide, across all 30 teams."""

    sort_column = getattr(Lineup, sort_by)
    direction = desc if order == "desc" else asc

    query = (
        select(Lineup, Team)
        .join(Team, Team.id == Lineup.team_id)
        .where(
            Lineup.season == season,
            Lineup.group_quantity == group_quantity,
            Lineup.minutes >= min_minutes,
        )
        .order_by(direction(sort_column))
        .limit(limit)
    )

    rows = session.execute(query).all()

    return {
        "filters": {
            "season": season,
            "group_quantity": group_quantity,
            "min_minutes": min_minutes,
            "sort_by": sort_by,
            "order": order,
            "limit": limit,
        },
        "count": len(rows),
        "lineups": [
            {
                "rank": i + 1,
                "group_name": lineup.group_name,
                "team_abbreviation": team.abbreviation,
                "team_full_name": team.full_name,
                "minutes": float(lineup.minutes) if lineup.minutes else None,
                "net_rating": float(lineup.net_rating) if lineup.net_rating else None,
                "off_rating": float(lineup.off_rating) if lineup.off_rating else None,
                "def_rating": float(lineup.def_rating) if lineup.def_rating else None,
            }
            for i, (lineup, team) in enumerate(rows)
        ],
    }