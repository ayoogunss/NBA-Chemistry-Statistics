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
import { fetchTeamLineups, fetchTeamLineupsForNetwork, type TeamLineupsResponse } from '../api/client';
import { TeamNetwork } from '../components/TeamNetwork';

export function TeamDetail() {
  const { teamId } = useParams<{ teamId: string }>();
  const id = Number(teamId);

  const chartQuery = useQuery<TeamLineupsResponse>({
    queryKey: ['team-lineups-chart', id],
    queryFn: () => fetchTeamLineups(id, { minMinutes: 500, limit: 15 }),
    enabled: Number.isFinite(id),
  });

  const networkQuery = useQuery<TeamLineupsResponse>({
    queryKey: ['team-lineups-network', id],
    queryFn: () => fetchTeamLineupsForNetwork(id),
    enabled: Number.isFinite(id),
  });

  const data = chartQuery.data;
  const networkData = networkQuery.data;
  const isLoading = chartQuery.isLoading || networkQuery.isLoading;
  const error = chartQuery.error || networkQuery.error;

  return (
    <div className="min-h-screen">
      <header className="border-b border-zinc-800">
        <div className="max-w-5xl mx-auto px-8 py-5 flex items-center gap-4">
          <Link to="/" className="text-sm text-zinc-500 hover:text-zinc-100 transition-colors">
            ← Teams
          </Link>
          <span className="text-sm text-zinc-700">/</span>
          <h1 className="text-base font-medium tracking-tight">
            {data?.team.full_name || 'Loading...'}
          </h1>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-8 py-10">
        {isLoading && <p className="text-zinc-400">Loading...</p>}
        {error && <p className="text-red-400">Error: {(error as Error).message}</p>}

        {data && networkData && (
          <>
            <div className="mb-8">
              <p className="text-xs uppercase tracking-wider text-zinc-500 mb-2">2025-26 Season</p>
              <h2 className="text-2xl font-medium tracking-tight">{data.team.full_name}</h2>
              <p className="text-sm text-zinc-400 mt-1">
                Chemistry network and lineup rankings for 2-man combinations.
              </p>
            </div>

            {/* Network Graph — the headline visualization */}
            <section className="mb-12">
              <div className="flex items-baseline justify-between mb-3">
                <h3 className="text-lg font-medium">Chemistry network</h3>
                <p className="text-xs text-zinc-500">
                  Edge color = net rating · Thickness = minutes together · Node size = total minutes
                </p>
              </div>
              <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
                <TeamNetwork lineups={networkData.lineups} />
              </div>
            </section>

            {/* Bar Chart — supporting view */}
            <section>
              <div className="flex items-baseline justify-between mb-3">
                <h3 className="text-lg font-medium">Top {data.count} Two-Man Lineups</h3>
                <p className="text-xs text-zinc-500">Minimum 500 minutes played together</p>
              </div>
              <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
                <div className="w-full" style={{ height: 520 }}>
                  <ResponsiveContainer>
                    <BarChart
                      data={data.lineups.map((l) => ({
                        ...l,
                        short_name: l.group_name
                          .split(' - ')
                          .map((n) => n.split(' ').slice(-1)[0])
                          .join(' / '),
                      }))}
                      layout="vertical"
                      margin={{ top: 10, right: 30, left: 140, bottom: 10 }}
                    >
                      <CartesianGrid strokeDasharray="2 4" stroke="#27272a" />
                      <XAxis
                        type="number"
                        stroke="#71717a"
                        tick={{ fill: '#a1a1aa', fontSize: 12 }}
                        label={{
                          value: 'Net Rating',
                          position: 'insideBottom',
                          offset: -5,
                          fill: '#71717a',
                          fontSize: 12,
                        }}
                      />
                      <YAxis
                        type="category"
                        dataKey="short_name"
                        width={140}
                        stroke="#71717a"
                        tick={{ fill: '#d4d4d8', fontSize: 12 }}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#18181b',
                          border: '1px solid #3f3f46',
                          borderRadius: 6,
                          fontSize: 12,
                        }}
                        labelStyle={{ color: '#f4f4f5', marginBottom: 4 }}
                        itemStyle={{ color: '#a1a1aa' }}
                        labelFormatter={(_label, payload) =>
                          payload && payload[0] ? payload[0].payload.group_name : ''
                        }
                        formatter={(value: number, _name, props) => [
                          `${value.toFixed(1)} (${props.payload.minutes} min)`,
                          'Net Rating',
                        ]}
                      />
                      <Bar dataKey="net_rating" radius={[0, 3, 3, 0]}>
                        {data.lineups.map((lineup, i) => (
                          <Cell
                            key={i}
                            fill={(lineup.net_rating ?? 0) >= 0 ? '#34d399' : '#f87171'}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}