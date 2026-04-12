import { useEffect, useState } from 'react';

interface MatchData {
  id: number;
  home_team: string;
  away_team: string;
  prob_home_win: number;
  prob_draw: number;
  prob_away_win: number;
  error?: string;
}

export default function DashboardPanel() {
  const [matches, setMatches] = useState<MatchData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/dashboard')
      .then(res => res.json())
      .then(data => {
        setMatches(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching dashboard data", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="flex-grow px-6 py-8 text-primary">Loading analytics...</div>;

  return (
    <main className="flex-grow overflow-y-auto px-6 py-8 bg-background">
      <div className="flex items-center gap-2 mb-6">
        <span className="material-symbols-outlined text-primary">sensors</span>
        <h2 className="text-2xl font-headline font-bold uppercase tracking-tight text-white">Live AI Fixtures</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {matches.map((match) => (
          match.error ? (
             <div key="err" className="text-red-500">Error: {match.error}</div>
          ) : (
            <div key={match.id} className="bg-surface-container-high rounded-xl p-6 relative overflow-hidden group border border-white/5">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <span className="font-bold text-sm text-white uppercase">{match.home_team.substring(0, 3)}</span>
                  <span className="text-on-surface-variant text-xs font-bold">VS</span>
                  <span className="font-bold text-sm text-white uppercase">{match.away_team.substring(0, 3)}</span>
                </div>
                <span className="text-[10px] font-bold text-primary bg-primary/10 px-2 py-1 rounded uppercase">PREMIER LEAGUE</span>
              </div>
              
              <div className="space-y-3">
                <p className="text-[10px] font-black text-on-surface-variant uppercase">AI 1X2 Probabilities</p>
                <div className="flex gap-2">
                  <button className="flex-1 bg-surface py-2 rounded text-center hover:bg-surface-bright border border-outline-variant/30">
                    <span className="block text-[8px] text-on-surface-variant mb-1">1 (HOME)</span>
                    <span className="font-headline font-bold text-xs text-primary">{(match.prob_home_win * 100).toFixed(1)}%</span>
                  </button>
                  <button className="flex-1 bg-surface py-2 rounded text-center hover:bg-surface-bright border border-outline-variant/30">
                    <span className="block text-[8px] text-on-surface-variant mb-1">X (DRAW)</span>
                    <span className="font-headline font-bold text-xs text-white">{(match.prob_draw * 100).toFixed(1)}%</span>
                  </button>
                  <button className="flex-1 bg-surface py-2 rounded text-center hover:bg-surface-bright border border-outline-variant/30">
                    <span className="block text-[8px] text-on-surface-variant mb-1">2 (AWAY)</span>
                    <span className="font-headline font-bold text-xs text-white">{(match.prob_away_win * 100).toFixed(1)}%</span>
                  </button>
                </div>
              </div>
            </div>
          )
        ))}
        {matches.length === 0 && <p className="text-on-surface-variant">No matches found in the datalake.</p>}
      </div>
    </main>
  );
}