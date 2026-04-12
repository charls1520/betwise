import { useState } from 'react';
import type { ChatMessage } from '../types';

export default function ChatPanel() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      role: "bot",
      content: "Analyzing Featured vs Opponent... I've detected a significant value spike on Featured to score next. The probability is 68% against odds of 2.45."
    }
  ]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg: ChatMessage = { id: Date.now().toString(), role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg.content, match_id: 1 })
      });
      const data = await response.json();
      
      const botMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "bot",
        content: data.response,
        sources: data.sources
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      setMessages(prev => [...prev, { id: Date.now().toString(), role: "bot", content: "Error connecting to the AI engine." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <aside className="fixed right-0 top-16 h-[calc(100vh-64px)] w-80 bg-[#102645]/90 backdrop-blur-2xl border-l border-white/5 flex-col hidden lg:flex shadow-[-10px_0px_30px_rgba(0,0,0,0.5)]">
      {/* Header */}
      <div className="p-6 border-b border-white/5">
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm font-bold text-[#47c4ff] uppercase font-['Space_Grotesk'] flex items-center gap-2">
            <span className="material-symbols-outlined text-lg">smart_toy</span>
            SOCCER AI ANALYST
          </span>
          <span className="flex items-center gap-1 text-[10px] text-[#6bff8f] font-bold">
            <span className="h-1.5 w-1.5 rounded-full bg-[#6bff8f] animate-pulse"></span>
            ACTIVE
          </span>
        </div>
        <p className="text-[10px] text-[#9eabc8] font-medium">Data-driven insights & value bets</p>
      </div>
      
      {/* Chat Area */}
      <div className="flex-grow overflow-y-auto p-4 space-y-4">
        {messages.map(msg => (
          <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            
            {/* Avatar */}
            {msg.role === 'user' ? (
              <div className="h-8 w-8 rounded-full overflow-hidden flex-shrink-0 bg-[#152c4e] flex items-center justify-center">
                 <span className="material-symbols-outlined text-sm text-white">person</span>
              </div>
            ) : (
              <div className="h-8 w-8 rounded-full bg-[#6bff8f]/20 flex items-center justify-center flex-shrink-0 border border-[#6bff8f]/20">
                <span className="material-symbols-outlined text-[#6bff8f] text-sm">precision_manufacturing</span>
              </div>
            )}

            {/* Message Bubble */}
            <div className={`${msg.role === 'user' ? 'bg-[#152c4e] rounded-tr-none' : 'bg-[#061934] rounded-tl-none'} rounded-lg p-3 max-w-[85%]`}>
              <p className={`text-[10px] font-bold mb-1 ${msg.role === 'user' ? 'text-[#6bff8f]' : 'text-[#47c4ff]'}`}>
                {msg.role === 'user' ? 'YOU' : 'KINETIC AI'}
              </p>
              <p className="text-xs text-[#dbe6ff] leading-relaxed">{msg.content}</p>
              
              {/* Rich Sources */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 space-y-2">
                  {msg.sources.map((src, idx) => (
                    <div className="bg-black/20 border border-[#6bff8f]/20 rounded p-2 mb-2" key={idx}>
                      <p className="text-[8px] text-[#6bff8f] font-bold uppercase mb-1">{src.type} Forecast</p>
                      <p className="text-[10px] text-white font-bold">{src.title || src.market}</p>
                      {src.snippet && <p className="text-[10px] text-[#6bff8f]">{src.snippet}</p>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
             <div className="h-8 w-8 rounded-full bg-[#6bff8f]/20 flex items-center justify-center flex-shrink-0 border border-[#6bff8f]/20">
              <span className="material-symbols-outlined text-[#6bff8f] text-sm animate-spin">autorenew</span>
            </div>
            <div className="bg-[#061934] rounded-lg rounded-tl-none p-3 max-w-[85%]">
              <p className="text-xs text-[#9eabc8] animate-pulse">Running tactical analysis...</p>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-white/5 bg-[#010e24]/50">
        <div className="relative group focus-within:ring-1 ring-[#6bff8f] rounded-lg">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !loading && handleSend()}
            placeholder="Ask AI Analyst..." 
            disabled={loading}
            className="w-full bg-[#061934] border-none focus:ring-0 rounded-lg text-sm py-3 pl-4 pr-12 text-[#dbe6ff] placeholder-[#9eabc8]/50 outline-none"
          />
          <button 
            onClick={handleSend} 
            disabled={loading}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-[#6bff8f] hover:scale-110 transition-transform disabled:opacity-50"
          >
            <span className="material-symbols-outlined">send</span>
          </button>
        </div>
        <div className="flex justify-between mt-3 px-1">
          <button className="text-[10px] font-bold text-[#9eabc8] hover:text-white flex items-center gap-1">
            <span className="material-symbols-outlined text-sm">terminal</span>
            <span className="hidden xl:inline">Match Engine</span>
          </button>
          <div className="flex gap-2 ml-auto">
            <a className="text-[#9eabc8] text-[10px] hover:text-white transition-colors" href="#">History</a>
            <a className="text-[#6bff8f] bg-[#152c4e] rounded px-2 text-[10px] transition-colors" href="#">Value Alerts</a>
          </div>
        </div>
      </div>
    </aside>
  );
}