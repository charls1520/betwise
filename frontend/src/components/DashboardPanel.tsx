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

  if (loading) return <div className="w-2/3 p-6">Loading dashboard...</div>;

  return (
    <div className="w-2/3 h-screen p-6 overflow-y-auto">
      <h2 className="text-2xl font-bold mb-4">Upcoming Matches (Live)</h2>
      <div className="space-y-4">
        {matches.map((match) => (
          match.error ? (
             <div key="err" className="text-red-500">Error: {match.error}</div>
          ) : (
            <div key={match.id} className="bg-white p-4 rounded shadow border-l-4 border-blue-500">
              <h3 className="text-lg font-semibold">{match.home_team} vs {match.away_team}</h3>
              <p className="text-gray-600 mb-2">ML Predictions (1X2)</p>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-blue-50 p-2 rounded text-center">
                  <span className="block text-xs text-gray-500">Home</span>
                  <span className="block text-lg font-bold">{(match.prob_home_win * 100).toFixed(1)}%</span>
                </div>
                <div className="bg-gray-50 p-2 rounded text-center">
                  <span className="block text-xs text-gray-500">Draw</span>
                  <span className="block text-lg font-bold">{(match.prob_draw * 100).toFixed(1)}%</span>
                </div>
                <div className="bg-red-50 p-2 rounded text-center">
                  <span className="block text-xs text-gray-500">Away</span>
                  <span className="block text-lg font-bold">{(match.prob_away_win * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          )
        ))}
        {matches.length === 0 && <p>No upcoming matches found.</p>}
      </div>
    </div>
  );
}