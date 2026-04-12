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

  if (loading) return <main className="flex-grow xl:ml-64 overflow-y-auto px-6 py-8 text-[#6bff8f]">Loading analytics...</main>;

  return (
    <main className="flex-grow xl:ml-64 overflow-y-auto px-6 py-8">
      {/* Hero Bento Header */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="md:col-span-2 relative group overflow-hidden rounded-xl bg-[#0b203d] p-8 min-h-[320px] flex flex-col justify-end">
          <div className="absolute inset-0 opacity-40 group-hover:scale-105 transition-transform duration-700 bg-gray-800">
            <div className="absolute inset-0 bg-gradient-to-t from-[#010e24] via-[#010e24]/60 to-transparent"></div>
          </div>
          <div className="relative z-10">
            <div className="flex items-center gap-2 mb-4">
              <span className="flex h-2 w-2 rounded-full bg-[#47c4ff] animate-pulse"></span>
              <span className="text-[#47c4ff] text-xs font-bold tracking-widest uppercase">Live: Featured Match</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-['Space_Grotesk'] font-bold text-white mb-2 leading-tight uppercase">Featured <span className="text-[#6bff8f]">vs</span> Opponent</h2>
            <p className="text-[#9eabc8] max-w-md mb-6">AI Prediction: Home side dominance expected in late transitions. XG projected at 2.45.</p>
            <div className="flex gap-4">
              <div className="bg-[#152c4e] px-6 py-3 rounded-lg border border-[#3b4861]/10">
                <p className="text-[10px] text-[#9eabc8] font-bold">1X2 ODDS (1)</p>
                <p className="text-2xl font-['Space_Grotesk'] font-bold text-[#6bff8f]">1.85</p>
              </div>
              <div className="bg-[#152c4e] px-6 py-3 rounded-lg border border-[#3b4861]/10">
                <p className="text-[10px] text-[#9eabc8] font-bold">O2.5 GOALS</p>
                <p className="text-2xl font-['Space_Grotesk'] font-bold text-white">1.72</p>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-[#0b203d] rounded-xl p-6 flex flex-col justify-between border-l-4 border-[#47c4ff]">
          <div>
            <h3 className="text-xs font-bold text-[#9eabc8] tracking-widest mb-4 uppercase">AI Accuracy Streak</h3>
            <div className="text-6xl font-['Space_Grotesk'] font-black text-white mb-2 tracking-tighter">92%</div>
            <p className="text-sm text-[#9eabc8]">Your current AI-guided prediction accuracy is elite. Unlock high-stake vaults.</p>
          </div>
          <div className="w-full h-2 bg-[#010e24] rounded-full overflow-hidden">
            <div className="h-full bg-[#47c4ff] w-[92%]"></div>
          </div>
        </div>
      </div>

      {/* AI-Powered Betting Suggestions */}
      <section className="mb-12">
        <div className="flex items-center gap-2 mb-6">
          <span className="material-symbols-outlined text-[#6bff8f]">psychology</span>
          <h2 className="text-2xl font-['Space_Grotesk'] font-bold uppercase tracking-tight text-white">AI Betting Suggestions</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-[#0b203d] to-[#010e24] p-5 rounded-xl border border-[#6bff8f]/10 relative">
            <div className="absolute top-4 right-4 bg-[#6bff8f]/20 text-[#6bff8f] text-[10px] font-bold px-2 py-1 rounded">94% CONFIDENCE</div>
            <p className="text-[10px] text-[#9eabc8] font-bold mb-1 uppercase">Corner Analysis</p>
            <h4 className="text-white font-bold mb-3">Over 9.5 Corners</h4>
            <p className="text-xs text-[#9eabc8] mb-4">High wing frequency detected in last 3 matches for both sides.</p>
            <button className="w-full bg-[#152c4e] py-2 rounded text-[#6bff8f] text-xs font-bold border border-[#6bff8f]/20 hover:bg-[#6bff8f] hover:text-[#002c0f] transition-all">ADD TO SLIP @ 1.95</button>
          </div>
          <div className="bg-gradient-to-br from-[#0b203d] to-[#010e24] p-5 rounded-xl border border-[#47c4ff]/10 relative">
            <div className="absolute top-4 right-4 bg-[#47c4ff]/20 text-[#47c4ff] text-[10px] font-bold px-2 py-1 rounded">88% CONFIDENCE</div>
            <p className="text-[10px] text-[#9eabc8] font-bold mb-1 uppercase">Card Market</p>
            <h4 className="text-white font-bold mb-3">Over 3.5 Total Cards</h4>
            <p className="text-xs text-[#9eabc8] mb-4">Referee tendency and derby tension suggest aggressive play.</p>
            <button className="w-full bg-[#152c4e] py-2 rounded text-[#47c4ff] text-xs font-bold border border-[#47c4ff]/20 hover:bg-[#47c4ff] hover:text-[#003044] transition-all">ADD TO SLIP @ 2.10</button>
          </div>
          <div className="bg-gradient-to-br from-[#0b203d] to-[#010e24] p-5 rounded-xl border border-[#6bff8f]/10 relative">
            <div className="absolute top-4 right-4 bg-[#6bff8f]/20 text-[#6bff8f] text-[10px] font-bold px-2 py-1 rounded">81% CONFIDENCE</div>
            <p className="text-[10px] text-[#9eabc8] font-bold mb-1 uppercase">Goal Forecast</p>
            <h4 className="text-white font-bold mb-3">Both Teams To Score</h4>
            <p className="text-xs text-[#9eabc8] mb-4">Defensive lapses identified in recent home fixtures.</p>
            <button className="w-full bg-[#152c4e] py-2 rounded text-[#6bff8f] text-xs font-bold border border-[#6bff8f]/20 hover:bg-[#6bff8f] hover:text-[#002c0f] transition-all">ADD TO SLIP @ 1.80</button>
          </div>
        </div>
      </section>

      {/* Featured Predictions Grid */}
      <div className="mb-12">
        <div className="flex justify-between items-end mb-6">
          <h2 className="text-2xl font-['Space_Grotesk'] font-bold uppercase tracking-tight text-white">Main Soccer Markets</h2>
          <a className="text-[#6bff8f] text-xs font-bold uppercase tracking-widest hover:underline" href="#">All Fixtures</a>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {matches.map((match) => (
            match.error ? (
              <div key="err" className="text-red-500">Error: {match.error}</div>
            ) : (
              <div key={match.id} className="bg-[#0b203d] rounded-xl p-6 relative overflow-hidden group border border-white/5">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-sm text-white">{match.home_team.substring(0, 3).toUpperCase()}</span>
                    <span className="text-[#9eabc8] text-xs font-bold">VS</span>
                    <span className="font-bold text-sm text-white">{match.away_team.substring(0, 3).toUpperCase()}</span>
                  </div>
                  <span className="text-[10px] font-bold text-[#6bff8f] bg-[#6bff8f]/10 px-2 py-1 rounded">PREMIER LEAGUE</span>
                </div>
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <p className="text-[10px] font-black text-[#9eabc8] uppercase">1X2 Full Time AI Probs</p>
                    <div className="flex gap-2">
                      <button className="flex-1 bg-[#010e24] p-2 rounded text-center hover:bg-[#152c4e] transition-colors">
                        <span className="block text-[8px] text-[#9eabc8]">1</span>
                        <span className="font-['Space_Grotesk'] font-bold text-xs text-[#6bff8f]">{(match.prob_home_win * 100).toFixed(1)}%</span>
                      </button>
                      <button className="flex-1 bg-[#010e24] p-2 rounded text-center hover:bg-[#152c4e] transition-colors">
                        <span className="block text-[8px] text-[#9eabc8]">X</span>
                        <span className="font-['Space_Grotesk'] font-bold text-xs text-white">{(match.prob_draw * 100).toFixed(1)}%</span>
                      </button>
                      <button className="flex-1 bg-[#010e24] p-2 rounded text-center hover:bg-[#152c4e] transition-colors">
                        <span className="block text-[8px] text-[#9eabc8]">2</span>
                        <span className="font-['Space_Grotesk'] font-bold text-xs text-white">{(match.prob_away_win * 100).toFixed(1)}%</span>
                      </button>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <p className="text-[10px] font-black text-[#9eabc8] uppercase">Total Goals</p>
                    <div className="flex gap-2">
                      <button className="flex-1 bg-[#010e24] p-2 rounded text-center hover:bg-[#152c4e] transition-colors">
                        <span className="block text-[8px] text-[#9eabc8]">O 2.5</span>
                        <span className="font-['Space_Grotesk'] font-bold text-xs text-white">{(match.prob_home_win * 1.5 * 100).toFixed(1)}%</span>
                      </button>
                      <button className="flex-1 bg-[#010e24] p-2 rounded text-center hover:bg-[#152c4e] transition-colors">
                        <span className="block text-[8px] text-[#9eabc8]">U 2.5</span>
                        <span className="font-['Space_Grotesk'] font-bold text-xs text-[#6bff8f]">{(match.prob_away_win * 100).toFixed(1)}%</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )
          ))}
          {matches.length === 0 && <p className="text-[#9eabc8]">No upcoming matches found.</p>}
        </div>
      </div>
    </main>
  );
}