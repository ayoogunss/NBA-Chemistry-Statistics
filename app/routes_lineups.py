"""
Endpoints for lineup chemistry data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, asc

from schema import Lineup, Team
from app.database import get_session

router = APIRouter(prefix="/teams/{team_id}/lineups", tags=["lineups"])


@router.get("/")
def list_team_lineups(
    team_id: int,
    season: str = Query("2025-26", description="Season in YYYY-YY format"),
    group_quantity: int = Query(2, ge=2, le=5, description="2, 3, or 5"),
    min_minutes: float = Query(100.0, ge=0, description="Filter to lineups with at least this many minutes"),
    sort_by: str = Query("net_rating", regex="^(net_rating|off_rating|def_rating|minutes)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    limit: int = Query(15, ge=1, le=100),
    session: Session = Depends(get_session),
):
    """Lineups for one team, with filtering and sorting."""

    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")

    sort_column = getattr(Lineup, sort_by)
    direction = desc if order == "desc" else asc

    query = (
        select(Lineup)
        .where(
            Lineup.team_id == team_id,
            Lineup.season == season,
            Lineup.group_quantity == group_quantity,
            Lineup.minutes >= min_minutes,
        )
        .order_by(direction(sort_column))
        .limit(limit)
    )

    lineups = session.execute(query).scalars().all()

    return {
        "team": {
            "id": team.id,
            "abbreviation": team.abbreviation,
            "full_name": team.full_name,
        },
        "filters": {
            "season": season,
            "group_quantity": group_quantity,
            "min_minutes": min_minutes,
            "sort_by": sort_by,
            "order": order,
            "limit": limit,
        },
        "count": len(lineups),
        "lineups": [
            {
                "group_name": l.group_name,
                "minutes": float(l.minutes) if l.minutes else None,
                "games_played": l.games_played,
                "net_rating": float(l.net_rating) if l.net_rating else None,
                "off_rating": float(l.off_rating) if l.off_rating else None,
                "def_rating": float(l.def_rating) if l.def_rating else None,
                "pace": float(l.pace) if l.pace else None,
            }
            for l in lineups
        ],
    }