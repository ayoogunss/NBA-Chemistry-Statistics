"""
Endpoints for player chemistry data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from schema import Player, Lineup, LineupPlayer, Team
from app.database import get_session

router = APIRouter(prefix="/players", tags=["players"])


@router.get("/{player_id}")
def get_player(player_id: int, session: Session = Depends(get_session)):
    """Get one player's basic info."""
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found")
    return {
        "id": player.id,
        "full_name": player.full_name,
        "display_name": player.display_name,
    }


@router.get("/{player_id}/chemistry")
def player_chemistry(
    player_id: int,
    season: str = Query("2025-26"),
    group_quantity: int = Query(2, ge=2, le=5),
    min_minutes: float = Query(100.0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    """All lineups a player appears in, sorted by net rating descending."""

    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found")

    # Find all lineup IDs containing this player
    query = (
        select(Lineup, Team)
        .join(LineupPlayer, LineupPlayer.lineup_id == Lineup.id)
        .join(Team, Team.id == Lineup.team_id)
        .where(
            LineupPlayer.player_id == player_id,
            Lineup.season == season,
            Lineup.group_quantity == group_quantity,
            Lineup.minutes >= min_minutes,
        )
        .order_by(desc(Lineup.net_rating))
        .limit(limit)
    )

    rows = session.execute(query).all()

    return {
        "player": {
            "id": player.id,
            "full_name": player.full_name,
            "display_name": player.display_name,
        },
        "filters": {
            "season": season,
            "group_quantity": group_quantity,
            "min_minutes": min_minutes,
            "limit": limit,
        },
        "count": len(rows),
        "lineups": [
            {
                "group_name": lineup.group_name,
                "team_abbreviation": team.abbreviation,
                "team_full_name": team.full_name,
                "minutes": float(lineup.minutes) if lineup.minutes else None,
                "net_rating": float(lineup.net_rating) if lineup.net_rating else None,
                "off_rating": float(lineup.off_rating) if lineup.off_rating else None,
                "def_rating": float(lineup.def_rating) if lineup.def_rating else None,
            }
            for lineup, team in rows
        ],
    }