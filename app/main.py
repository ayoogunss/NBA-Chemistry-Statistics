"""
FastAPI app entry point. Wires up all the routers.
"""

from fastapi import FastAPI
from app.routes_teams import router as teams_router
from app.routes_lineups import router as lineups_router
from app.routes_players import router as players_router
from app.routes_leaderboard import router as leaderboard_router

app = FastAPI(
    title="NBA Chemistry API",
    description="League-wide 2-man lineup chemistry data",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}


app.include_router(teams_router)
app.include_router(lineups_router)
app.include_router(players_router)
app.include_router(leaderboard_router)