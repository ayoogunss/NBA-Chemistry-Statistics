import { useMemo, useRef, useEffect, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import type { Lineup } from '../api/client';

type Props = {
  lineups: Lineup[];
};

type GraphNode = {
  id: string;
  totalMinutes: number;
};

type GraphLink = {
  source: string;
  target: string;
  netRating: number;
  minutes: number;
  groupName: string;
};

function shortName(fullName: string): string {
  const parts = fullName.trim().split(' ');
  return parts[parts.length - 1];
}

function parsePlayers(groupName: string): [string, string] | null {
  const parts = groupName.split(' - ');
  if (parts.length !== 2) return null;
  return [parts[0].trim(), parts[1].trim()];
}

export function TeamNetwork({ lineups }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<any>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: 600,
        });
      }
    };
    updateSize();
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, []);

  const graphData = useMemo(() => {
    const nodeMap = new Map<string, GraphNode>();
    const links: GraphLink[] = [];

    for (const lineup of lineups) {
      const players = parsePlayers(lineup.group_name);
      if (!players) continue;
      const [a, b] = players;
      const minutes = lineup.minutes ?? 0;

      for (const player of [a, b]) {
        const existing = nodeMap.get(player);
        if (existing) {
          existing.totalMinutes += minutes;
        } else {
          nodeMap.set(player, { id: player, totalMinutes: minutes });
        }
      }

      links.push({
        source: a,
        target: b,
        netRating: lineup.net_rating ?? 0,
        minutes,
        groupName: lineup.group_name,
      });
    }

    return {
      nodes: Array.from(nodeMap.values()),
      links,
    };
  }, [lineups]);

  const maxMinutes = Math.max(...graphData.nodes.map((n) => n.totalMinutes), 1);
  const maxEdgeMinutes = Math.max(...graphData.links.map((l) => l.minutes), 1);

  // Configure physics once the graph is mounted
  useEffect(() => {
    const g = graphRef.current;
    if (!g) return;
    // Spread nodes further apart by increasing repulsion
    g.d3Force('charge')?.strength(-400);
    // Make edges longer
    g.d3Force('link')?.distance(120);
  }, []);

  return (
    <div ref={containerRef} className="w-full">
      <ForceGraph2D
        ref={graphRef}
        graphData={graphData}
        width={dimensions.width}
        height={dimensions.height}
        backgroundColor="#18181b"
        nodeRelSize={1}
        nodeColor={() => '#e4e4e7'}
        linkColor={(link: any) => (link.netRating >= 0 ? '#34d399' : '#f87171')}
        linkWidth={(link: any) => 0.5 + (link.minutes / maxEdgeMinutes) * 3.5}
        linkOpacity={0.55}
        linkLabel={(link: any) =>
          `${link.groupName}: ${link.netRating.toFixed(1)} net rating, ${Math.round(link.minutes)} min`
        }
        nodeCanvasObject={(node: any, ctx, globalScale) => {
          const label = shortName(node.id);
          const fontSize = 11 / globalScale;
          // Tighter range: 5px to 12px
          const radius = 5 + (node.totalMinutes / maxMinutes) * 7;

          // Node circle
          ctx.beginPath();
          ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI);
          ctx.fillStyle = '#e4e4e7';
          ctx.fill();
          ctx.strokeStyle = '#3f3f46';
          ctx.lineWidth = 1.5 / globalScale;
          ctx.stroke();

          // Label background (helps with overlap readability)
          ctx.font = `500 ${fontSize}px Inter, system-ui, sans-serif`;
          const textWidth = ctx.measureText(label).width;
          const padding = 3 / globalScale;
          const labelY = node.y + radius + 4 / globalScale;

          ctx.fillStyle = 'rgba(24, 24, 27, 0.85)';
          ctx.fillRect(
            node.x - textWidth / 2 - padding,
            labelY - padding,
            textWidth + padding * 2,
            fontSize + padding * 2
          );

          // Label text
          ctx.textAlign = 'center';
          ctx.textBaseline = 'top';
          ctx.fillStyle = '#f4f4f5';
          ctx.fillText(label, node.x, labelY);
        }}
        nodePointerAreaPaint={(node: any, color, ctx) => {
          const radius = 5 + (node.totalMinutes / maxMinutes) * 7;
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI);
          ctx.fill();
        }}
        cooldownTicks={150}
      />
    </div>
  );
}