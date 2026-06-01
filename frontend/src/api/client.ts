const API_BASE = 'http://localhost:8000';

export type Team = {
  id: number;
  abbreviation: string;
  full_name: string;
};

export type Lineup = {
  group_name: string;
  minutes: number | null;
  games_played: number | null;
  net_rating: number | null;
  off_rating: number | null;
  def_rating: number | null;
  pace: number | null;
};

export type TeamLineupsResponse = {
  team: Team;
  filters: Record<string, unknown>;
  count: number;
  lineups: Lineup[];
};

export async function fetchTeams(): Promise<Team[]> {
  const res = await fetch(`${API_BASE}/teams/`);
  if (!res.ok) throw new Error('Failed to fetch teams');
  return res.json();
}

export async function fetchTeamLineups(
  teamId: number,
  params: { minMinutes?: number; limit?: number } = {}
): Promise<TeamLineupsResponse> {
  const search = new URLSearchParams();
  if (params.minMinutes !== undefined) search.set('min_minutes', String(params.minMinutes));
  if (params.limit !== undefined) search.set('limit', String(params.limit));

  const url = `${API_BASE}/teams/${teamId}/lineups/?${search.toString()}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch lineups');
  return res.json();
}

export async function fetchTeamLineupsForNetwork(teamId: number): Promise<TeamLineupsResponse> {
  // For the network graph: lower threshold, higher limit, sorted by minutes
  // (so we get the team's most-used pairings, not the highest net rating outliers)
  const url = `${API_BASE}/teams/${teamId}/lineups/?min_minutes=200&limit=100&sort_by=minutes&order=desc`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch lineups');
  return res.json();
}