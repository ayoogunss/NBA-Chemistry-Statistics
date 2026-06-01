import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { fetchTeams, type Team } from '../api/client';

export function TeamsList() {
  const { data, isLoading, error } = useQuery<Team[]>({
    queryKey: ['teams'],
    queryFn: fetchTeams,
  });

  return (
    <div className="min-h-screen">
      <header className="border-b border-zinc-800">
        <div className="max-w-5xl mx-auto px-8 py-5">
          <h1 className="text-base font-medium tracking-tight">NBA Chemistry</h1>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-8 py-10">
        <div className="mb-8">
          <h2 className="text-2xl font-medium tracking-tight">Teams</h2>
          <p className="text-sm text-zinc-400 mt-1">
            Pick a team to see its 2-man lineup chemistry.
          </p>
        </div>

        {isLoading && <p className="text-zinc-400">Loading teams...</p>}
        {error && <p className="text-red-400">Error: {(error as Error).message}</p>}

        {data && (
          <div className="border border-zinc-800 rounded-lg overflow-hidden">
            {data.map((team, i) => (
              <Link
                key={team.id}
                to={`/teams/${team.id}`}
                className={`flex items-center justify-between px-5 py-4 hover:bg-zinc-900 transition-colors ${
                  i !== data.length - 1 ? 'border-b border-zinc-800' : ''
                }`}
              >
                <span className="text-zinc-100">{team.full_name}</span>
                <span className="text-xs font-mono text-zinc-500 tracking-wider">
                  {team.abbreviation}
                </span>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}