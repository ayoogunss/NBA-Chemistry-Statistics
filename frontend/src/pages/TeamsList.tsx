import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { fetchTeams, type Team } from '../api/client';

export function TeamsList() {
  const { data, isLoading, error } = useQuery<Team[]>({
    queryKey: ['teams'],
    queryFn: fetchTeams,
  });

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif', maxWidth: 600 }}>
      <h1 style={{ marginBottom: '0.25rem' }}>NBA Chemistry</h1>
      <p style={{ color: '#666', marginTop: 0, marginBottom: '1.5rem' }}>
        Pick a team to see its 2-man lineup chemistry.
      </p>

      {isLoading && <p>Loading teams...</p>}
      {error && <p style={{ color: 'crimson' }}>Error: {(error as Error).message}</p>}

      {data && (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {data.map((team) => (
            <li key={team.id} style={{ borderBottom: '1px solid #eee' }}>
              <Link
                to={`/teams/${team.id}`}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  padding: '0.75rem 1rem',
                  textDecoration: 'none',
                  color: '#111',
                }}
              >
                <span>{team.full_name}</span>
                <span style={{ color: '#888', fontFamily: 'monospace' }}>{team.abbreviation}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}