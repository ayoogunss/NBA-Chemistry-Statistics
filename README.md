# NBA CHEMISTRY STATISTICS
This is a web app that helps visualize a team duo's chemistry for all 30 NBA teams throughout the 2025-26 season.

## Technology Stack
- **THE BACKEND**: Python, FastAPI, PostgreSQL (on Supabase)
- **THE FRONTEND**: React, TypeScript, Vite, and Tailwind CSS
- **VISUAL EFFECTS**: Recharts (Bar Graphs), react-force-graph-2d
- **DATA SOURCE**: NBA Statistics API (using *nba_api*)

## App Features
- Chemistry Network graph established for each team, where great chemistry between a duo create clusters and rotation outliers (players possibly benched frequently) hover near the edges
- A Bar Graph that ranks a team's top duo based on their net rating (including a 500+ minute filter)
- A schema (including teams, players, lineups) that essentially supports league-wide queries
- Large data pipeline that includes retry logic while holding 4500 lineup records througout the 30 NBA teams

## The Architecture 
- *app/* — essentially the backend holding REST endpoints for teams, players, and the league leaderboard
- *frontend/* — React and TypeScript application taking in information from the API 
- *fetch_lineups.py* | *fetch_all_teams.py* — Taking in information from data pipeline

## Project Status 
Still in development. Current aspects have been completed
- Data foundation
- The frontend holding visuals for chemistry bar and network graphs
- API Data pulling