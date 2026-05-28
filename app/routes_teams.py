"""
Endpoints for team data.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from schema import Team
from app.database import get_session

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("/")
def list_teams(session: Session = Depends(get_session)):
    """List all 30 NBA teams."""
    teams = session.execute(select(Team).order_by(Team.full_name)).scalars().all()
    return [
        {"id": t.id, "abbreviation": t.abbreviation, "full_name": t.full_name}
        for t in teams
    ]


@router.get("/{team_id}")
def get_team(team_id: int, session: Session = Depends(get_session)):
    """Get one team by NBA team ID."""
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
    return {
        "id": team.id,
        "abbreviation": team.abbreviation,
        "full_name": team.full_name,
    }