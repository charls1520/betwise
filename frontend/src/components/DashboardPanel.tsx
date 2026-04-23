import { useEffect, useState } from 'react';

interface MatchData {
  id: number;
  home_team: string;
  away_team: string;
  prob_home_win: number;
  prob_draw: number;
  prob_away_win: number;
  home_odds: number;
  home_edge: number;
  match_time?: string;
  league?: string;
  error?: string;
}

interface Suggestion {
  market: string;
  match: string;
  confidence: string;
  edge: string;
  odds: number;
  reasoning: string;
}

interface DashboardPayload {
  matches: MatchData[];
  suggestions: Suggestion[];
  error?: string;
}

const formatToUTC5 = (utcTimeString: string | undefined) => {
  if (!utcTimeString || utcTimeString === "TBA") return "TBA";
  try {
    const date = new Date(utcTimeString);
    return date.toLocaleString("es-CO", {
      timeZone: "America/Bogota",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true
    });
  } catch (e) {
    return utcTimeString;
  }
};

export default function DashboardPanel({ isNavOpen, isChatOpen }: { isNavOpen?: boolean, isChatOpen?: boolean }) {
  const [data, setData] = useState<DashboardPayload | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || '';
    fetch(`${apiUrl}/api/dashboard`)
      .then(res => res.json())
      .then(fetchedData => {
        // Handle case where error is returned as list of dicts from old format
        if (Array.isArray(fetchedData) && fetchedData.length > 0 && fetchedData[0].error) {
           setData({ matches: [], suggestions: [], error: fetchedData[0].error });
        } else {
           setData(fetchedData as DashboardPayload);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching dashboard data", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <main className={`flex-grow overflow-y-auto px-6 py-8 text-[#6bff8f] transition-all duration-300 ${isNavOpen ? 'ml-64' : 'ml-0'} ${isChatOpen ? 'mr-80' : 'mr-0'}`}>Cargando analíticas...</main>;
  if (data?.error) return <div className="text-red-500 p-8">Error: {data.error}</div>;
  if (!data) return <div className="text-white p-8">No hay datos disponibles</div>;

  const matches = data.matches || [];
  const suggestions = data.suggestions || [];

  return (
    <main className={`flex-grow overflow-y-auto px-6 py-8 transition-all duration-300 ${isNavOpen ? 'ml-64' : 'ml-0'} ${isChatOpen ? 'mr-80' : 'mr-0'}`}>
      {matches.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="md:col-span-2 relative group overflow-hidden rounded-xl bg-[#0b203d] p-8 min-h-[320px] flex flex-col justify-end">
            <div className="absolute inset-0 opacity-40 group-hover:scale-105 transition-transform duration-700 bg-gray-800">
              <div className="absolute inset-0 bg-gradient-to-t from-[#010e24] via-[#010e24]/60 to-transparent"></div>
            </div>
            <div className="relative z-10">
              <div className="flex items-center gap-2 mb-4">
                <span className="flex h-2 w-2 rounded-full bg-[#47c4ff] animate-pulse"></span>
                <span className="text-[#47c4ff] text-xs font-bold tracking-widest uppercase">En Vivo: Partido Destacado</span>
              </div>
              <h2 className="text-4xl md:text-5xl font-['Space_Grotesk'] font-bold text-white mb-2 leading-tight uppercase">{matches[0].home_team} <span className="text-[#6bff8f]">vs</span> {matches[0].away_team}</h2>
              <p className="text-[#9eabc8] max-w-md mb-6">Predicción de IA: Cálculo ML en tiempo real basado en datos históricos de xG.</p>
              <div className="flex gap-4">
                <div className="bg-[#152c4e] px-6 py-3 rounded-lg border border-[#3b4861]/10">
                  <p className="text-[10px] text-[#9eabc8] font-bold">1 (LOCAL) PROB</p>
                  <p className="text-2xl font-['Space_Grotesk'] font-bold text-[#6bff8f]">{(matches[0].prob_home_win * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-[#152c4e] px-6 py-3 rounded-lg border border-[#3b4861]/10">
                  <p className="text-[10px] text-[#9eabc8] font-bold">EDGE (MARGEN)</p>
                  <p className="text-2xl font-['Space_Grotesk'] font-bold text-white">{(matches[0].home_edge * 100).toFixed(1)}%</p>
                </div>
              </div>
            </div>
          </div>
          <div className="bg-[#0b203d] rounded-xl p-6 flex flex-col justify-between border-l-4 border-[#47c4ff]">
            <div>
              <h3 className="text-xs font-bold text-[#9eabc8] tracking-widest mb-4 uppercase">Racha de Precisión IA</h3>
              <div className="text-6xl font-['Space_Grotesk'] font-black text-white mb-2 tracking-tighter">92%</div>
              <p className="text-sm text-[#9eabc8]">Tu precisión actual guiada por IA es élite. Desbloquea apuestas de alto valor.</p>
            </div>
            <div className="w-full h-2 bg-[#010e24] rounded-full overflow-hidden">
              <div className="h-full bg-[#47c4ff] w-[92%]"></div>
            </div>
          </div>
        </div>
      )}

      {/* AI-Powered Betting Suggestions */}
      <section className="mb-12">
        <div className="flex items-center gap-2 mb-6">
          <span className="material-symbols-outlined text-[#6bff8f]">psychology</span>
          <h2 className="text-2xl font-['Space_Grotesk'] font-bold uppercase tracking-tight text-white">Apuestas de Valor Verificadas</h2>
        </div>
        
        {suggestions.length === 0 ? (
            <div className="bg-[#0b203d] p-6 rounded-xl border border-[#3b4861] text-center">
                <p className="text-[#9eabc8] text-sm">No se encontraron apuestas de alto valor que superen el filtro estricto del 10% hoy. Protege tu saldo.</p>
            </div>
        ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {suggestions.map((sug, i) => (
                <div key={i} className="bg-gradient-to-br from-[#0b203d] to-[#010e24] p-5 rounded-xl border border-[#6bff8f]/10 relative">
                <div className="absolute top-4 right-4 bg-[#6bff8f]/20 text-[#6bff8f] text-[10px] font-bold px-2 py-1 rounded">{sug.confidence} CONFIANZA</div>
                <p className="text-[10px] text-[#9eabc8] font-bold mb-1 uppercase">{sug.match}</p>
                <h4 className="text-white font-bold mb-3">{sug.market}</h4>
                <p className="text-xs text-[#9eabc8] mb-4">{sug.reasoning} (Margen: {sug.edge})</p>
                <button className="w-full bg-[#152c4e] py-2 rounded text-[#6bff8f] text-xs font-bold border border-[#6bff8f]/20 hover:bg-[#6bff8f] hover:text-[#002c0f] transition-all">AÑADIR AL TICKET @ {sug.odds}</button>
                </div>
            ))}
            </div>
        )}
      </section>

      {/* Featured Predictions Grid */}
      <div className="mb-12">
        <div className="flex justify-between items-end mb-6">
          <h2 className="text-2xl font-['Space_Grotesk'] font-bold uppercase tracking-tight text-white">Mercados Principales</h2>
          <a className="text-[#6bff8f] text-xs font-bold uppercase tracking-widest hover:underline" href="#">Todos los Partidos</a>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {matches.map((match) => (
            match.error ? (
              <div key="err" className="text-red-500">Error: {match.error}</div>
            ) : (
              <div key={match.id} className="bg-[#0b203d] rounded-xl p-6 relative overflow-hidden group border border-white/5">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex flex-col">
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-sm text-white">{match.home_team}</span>
                      <span className="text-[#9eabc8] text-xs font-bold">VS</span>
                      <span className="font-bold text-sm text-white">{match.away_team}</span>
                    </div>
                    <span className="text-[#9eabc8] text-[10px] mt-1">{formatToUTC5(match.match_time)}</span>
                  </div>
                  <span className="text-[10px] font-bold text-[#6bff8f] bg-[#6bff8f]/10 px-2 py-1 rounded truncate max-w-[120px]" title={match.league || "PREMIER LEAGUE"}>{match.league || "PREMIER LEAGUE"}</span>
                </div>
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <p className="text-[10px] font-black text-[#9eabc8] uppercase">Probabilidades IA 1X2 Final</p>
                    <div className="flex gap-2">
                      <button className="flex-1 bg-[#010e24] p-2 rounded text-center hover:bg-[#152c4e] transition-colors">
                        <span className="block text-[8px] text-[#9eabc8]">1</span>
                        <span className={`font-['Space_Grotesk'] font-bold text-xs ${Math.max(match.prob_home_win, match.prob_draw, match.prob_away_win) === match.prob_home_win ? 'text-[#6bff8f]' : 'text-white'}`}>{(match.prob_home_win * 100).toFixed(1)}%</span>
                      </button>
                      <button className="flex-1 bg-[#010e24] p-2 rounded text-center hover:bg-[#152c4e] transition-colors">
                        <span className="block text-[8px] text-[#9eabc8]">X</span>
                        <span className={`font-['Space_Grotesk'] font-bold text-xs ${Math.max(match.prob_home_win, match.prob_draw, match.prob_away_win) === match.prob_draw ? 'text-[#6bff8f]' : 'text-white'}`}>{(match.prob_draw * 100).toFixed(1)}%</span>
                      </button>
                      <button className="flex-1 bg-[#010e24] p-2 rounded text-center hover:bg-[#152c4e] transition-colors">
                        <span className="block text-[8px] text-[#9eabc8]">2</span>
                        <span className={`font-['Space_Grotesk'] font-bold text-xs ${Math.max(match.prob_home_win, match.prob_draw, match.prob_away_win) === match.prob_away_win ? 'text-[#6bff8f]' : 'text-white'}`}>{(match.prob_away_win * 100).toFixed(1)}%</span>
                      </button>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <p className="text-[10px] font-black text-[#9eabc8] uppercase">Goles Totales</p>
                    <div className="flex gap-2">
                      <button className="flex-1 bg-[#010e24] p-2 rounded text-center hover:bg-[#152c4e] transition-colors">
                        <span className="block text-[8px] text-[#9eabc8]">MÁS 2.5</span>
                        <span className={`font-['Space_Grotesk'] font-bold text-xs ${(match.prob_home_win * 1.5) > match.prob_away_win ? 'text-[#6bff8f]' : 'text-white'}`}>{(match.prob_home_win * 1.5 * 100).toFixed(1)}%</span>
                      </button>
                      <button className="flex-1 bg-[#010e24] p-2 rounded text-center hover:bg-[#152c4e] transition-colors">
                        <span className="block text-[8px] text-[#9eabc8]">MENOS 2.5</span>
                        <span className={`font-['Space_Grotesk'] font-bold text-xs ${match.prob_away_win > (match.prob_home_win * 1.5) ? 'text-[#6bff8f]' : 'text-white'}`}>{(match.prob_away_win * 100).toFixed(1)}%</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )
          ))}
          {matches.length === 0 && <p className="text-[#9eabc8]">No se encontraron próximos partidos.</p>}
        </div>
      </div>
    </main>
  );
}