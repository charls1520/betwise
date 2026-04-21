import { useState } from 'react';
import DashboardPanel from './components/DashboardPanel';
import ChatPanel from './components/ChatPanel';
import AuditModal from './components/AuditModal';

function App() {
  const [isAuditOpen, setIsAuditOpen] = useState(false);
  const [isNavOpen, setIsNavOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <div className="flex bg-[#010e24] h-screen overflow-hidden text-[#dbe6ff] font-['Manrope']">
      {/* Top Navigation Bar */}
      <header className="fixed top-0 w-full z-50 bg-[#102645]/80 backdrop-blur-xl shadow-2xl shadow-black/40">
        <div className="flex justify-between items-center px-6 h-16 w-full max-w-screen-2xl mx-auto">
          <div className="flex items-center gap-8">
            <button onClick={() => setIsNavOpen(!isNavOpen)} className="p-2 text-[#9eabc8] hover:text-[#6bff8f] transition-colors xl:hidden">
              <span className="material-symbols-outlined">menu</span>
            </button>
            <span className="text-2xl font-bold tracking-tighter text-[#6bff8f] uppercase font-['Space_Grotesk']">THE KINETIC VAULT</span>
            <nav className="hidden md:flex gap-6">
              <a className="text-[#6bff8f] border-b-2 border-[#6bff8f] pb-1 font-['Space_Grotesk'] tracking-tight" href="#">FÚTBOL</a>
              <a className="text-[#9eabc8] font-medium hover:text-white transition-colors duration-200" href="#">PARTIDOS EN VIVO</a>
              <a className="text-[#9eabc8] font-medium hover:text-white transition-colors duration-200" href="#">ANÁLISIS IA</a>
              <a className="text-[#9eabc8] font-medium hover:text-white transition-colors duration-200" href="#">PROMOS</a>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <div className="relative bg-[#0b203d] px-4 py-2 rounded-lg hidden lg:flex items-center gap-2">
              <span className="material-symbols-outlined text-[#9eabc8] text-sm">search</span>
              <input className="bg-transparent border-none focus:ring-0 text-sm p-0 w-48 text-[#dbe6ff] outline-none" placeholder="Buscar ligas..." type="text" />
            </div>
            <div className="flex items-center gap-3">
              <button onClick={() => setIsChatOpen(!isChatOpen)} className="p-2 text-[#9eabc8] hover:text-[#6bff8f] transition-colors lg:hidden" title="Toggle Chat">
                <span className="material-symbols-outlined">chat</span>
              </button>
              <button className="p-2 text-[#9eabc8] hover:text-[#6bff8f] transition-colors">
                <span className="material-symbols-outlined">notifications</span>
              </button>
              <button onClick={() => setIsAuditOpen(true)} className="p-2 text-[#9eabc8] hover:text-[#6bff8f] transition-colors" title="System Audit">
                <span className="material-symbols-outlined">analytics</span>
              </button>
              <div className="h-8 w-8 rounded-full overflow-hidden bg-[#152c4e] flex items-center justify-center">
                <span className="material-symbols-outlined text-sm text-white">person</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* App Layout Container */}
      <div className="flex pt-16 h-screen w-full">
        {/* Sidebar Left: Soccer Navigation */}
        <aside className={`fixed left-0 top-16 h-[calc(100vh-64px)] w-64 bg-[#02132b] flex-col py-6 overflow-y-auto transition-transform duration-300 z-40 flex ${isNavOpen ? 'translate-x-0' : '-translate-x-full'}`}>
          <div className="px-6 mb-8">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-lg font-black text-[#6bff8f] font-['Space_Grotesk']">CENTRO DE FÚTBOL</span>
              <div className="bg-[#6bff8f]/20 text-[#6bff8f] text-[10px] px-1.5 py-0.5 rounded font-bold uppercase">AI PRO</div>
            </div>
            <p className="text-[10px] text-[#9eabc8] font-bold tracking-widest">FILTROS TÁCTICOS</p>
          </div>
          <nav className="flex-grow space-y-1">
            <a className="flex items-center gap-3 bg-[#0b203d] text-[#6bff8f] rounded-r-full py-3 px-6 border-l-4 border-[#6bff8f] translate-x-1 transition-transform" href="#">
              <span className="material-symbols-outlined">sensors</span>
              <span className="font-medium">Partidos en Vivo</span>
            </a>
            <a className="flex items-center gap-3 text-[#9eabc8] py-3 px-6 hover:bg-[#0b203d]/50 hover:text-white transition-all" href="#">
              <span className="material-symbols-outlined">today</span>
              <span className="font-medium">Jornada de Hoy</span>
            </a>
            <a className="flex items-center gap-3 text-[#9eabc8] py-3 px-6 hover:bg-[#0b203d]/50 hover:text-white transition-all" href="#">
              <span className="material-symbols-outlined">upcoming</span>
              <span className="font-medium">Próximos Eventos</span>
            </a>
            <div className="pt-6 px-6 pb-2">
              <p className="text-[10px] text-[#9eabc8] font-bold tracking-widest uppercase">Ligas Élite</p>
            </div>
            <a className="flex items-center gap-3 text-[#9eabc8] py-3 px-6 hover:bg-[#0b203d]/50 hover:text-white transition-all" href="#">
              <span className="material-symbols-outlined">emoji_events</span>
              <span className="font-medium">Champions League</span>
            </a>
            <a className="flex items-center gap-3 text-[#9eabc8] py-3 px-6 hover:bg-[#0b203d]/50 hover:text-white transition-all" href="#">
              <span className="material-symbols-outlined">sports_soccer</span>
              <span className="font-medium">Premier League</span>
            </a>
            <a className="flex items-center gap-3 text-[#9eabc8] py-3 px-6 hover:bg-[#0b203d]/50 hover:text-white transition-all" href="#">
              <span className="material-symbols-outlined">flag</span>
              <span className="font-medium">La Liga</span>
            </a>
          </nav>
          <div className="px-6 mt-auto">
            <button className="w-full bg-gradient-to-r from-[#6bff8f] to-[#0abc56] text-[#002c0f] font-extrabold py-4 rounded-lg shadow-lg shadow-[#6bff8f]/20 hover:scale-95 duration-150 ease-in-out uppercase text-xs tracking-tighter">
              CREADOR DE TICKETS INSTANTÁNEO
            </button>
          </div>
        </aside>

        {/* Main Feed and Right Sidebar Container */}
        <DashboardPanel isNavOpen={isNavOpen} isChatOpen={isChatOpen} />
        <ChatPanel isOpen={isChatOpen} />
      </div>
      <AuditModal isOpen={isAuditOpen} onClose={() => setIsAuditOpen(false)} />
    </div>
  );
}

export default App;