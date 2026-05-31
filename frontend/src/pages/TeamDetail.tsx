import { useQuery } from '@tanstack/react-query';
import { Link, useParams } from 'react-router-dom';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Cell,
} from 'recharts';
import { fetchTeamLineups, type TeamLineupsResponse } from '../api/client';

export function TeamDetail() {
  const { teamId } = useParams<{ teamId: string }>();
  const id = Number(teamId);

  const { data, isLoading, error } = useQuery<TeamLineupsResponse>({
    queryKey: ['team-lineups', id],
    queryFn: () => fetchTeamLineups(id, { minMinutes: 100, limit: 15 }),
    enabled: Number.isFinite(id),
  });

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif', maxWidth: 900 }}>
      <Link to="/" style={{ color: '#666', textDecoration: 'none' }}>
        ← back to teams
      </Link>

      {isLoading && <p>Loading...</p>}
      {error && <p style={{ color: 'crimson' }}>Error: {(error as Error).message}</p>}

      {data && (
        <>
          <h1 style={{ marginBottom: '0.25rem', marginTop: '1rem' }}>{data.team.full_name}</h1>
          <p style={{ color: '#666', marginTop: 0 }}>
            Top {data.count} two-man lineups by net rating (100+ minutes together)
          </p>

          <div style={{ width: '100%', height: 500, marginTop: '2rem' }}>
            <ResponsiveContainer>
              <BarChart
                data={data.lineups}
                layout="vertical"
                margin={{ top: 10, right: 30, left: 160, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis type="category" dataKey="group_name" width={150} />
                <Tooltip
                  formatter={(value: number, _name, props) => [
                    `${value.toFixed(1)} net rating`,
                    `${props.payload.minutes} min`,
                  ]}
                />
                <Bar dataKey="net_rating">
                  {data.lineups.map((lineup, i) => (
                    <Cell
                      key={i}
                      fill={(lineup.net_rating ?? 0) >= 0 ? '#1D9E75' : '#A32D2D'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}