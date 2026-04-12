// frontend/src/components/ChatPanel.tsx
import { useState } from 'react';
import type { ChatMessage } from '../types';

export default function ChatPanel() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      role: "bot",
      content: "System online. I am your Soccer AI Analyst. What matches are we analyzing today?"
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
    <aside className="w-80 h-screen bg-surface-container-high/90 backdrop-blur-2xl border-l border-white/5 flex flex-col flex-shrink-0 shadow-[-10px_0px_30px_rgba(0,0,0,0.5)]">
      {/* Header */}
      <div className="p-6 border-b border-white/5">
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm font-bold text-tertiary uppercase font-headline flex items-center gap-2">
            <span className="material-symbols-outlined text-lg">smart_toy</span>
            AI ANALYST
          </span>
          <span className="flex items-center gap-1 text-[10px] text-primary font-bold">
            <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse"></span>
            ACTIVE
          </span>
        </div>
        <p className="text-[10px] text-on-surface-variant font-medium">BetWise RAG Engine powered by Gemma</p>
      </div>
      
      {/* Chat Area */}
      <div className="flex-grow overflow-y-auto p-4 space-y-6">
        {messages.map(msg => (
          <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            
            {/* Avatar */}
            <div className={`h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 border ${msg.role === 'user' ? 'bg-surface-bright border-outline-variant' : 'bg-primary/20 border-primary/20'}`}>
              <span className={`material-symbols-outlined text-sm ${msg.role === 'user' ? 'text-white' : 'text-primary'}`}>
                {msg.role === 'user' ? 'person' : 'precision_manufacturing'}
              </span>
            </div>

            {/* Message Bubble */}
            <div className={`${msg.role === 'user' ? 'bg-surface-bright rounded-tr-none' : 'bg-surface-container rounded-tl-none'} rounded-lg p-3 max-w-[80%] border border-white/5`}>
              <p className={`text-[10px] font-bold mb-1 uppercase ${msg.role === 'user' ? 'text-white' : 'text-tertiary'}`}>
                {msg.role === 'user' ? 'YOU' : 'KINETIC AI'}
              </p>
              <p className="text-xs text-on-surface leading-relaxed whitespace-pre-wrap">{msg.content}</p>
              
              {/* Rich Sources */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 space-y-2">
                  {msg.sources.map((src, idx) => (
                    <div key={idx} className="bg-black/20 border border-primary/20 rounded p-2">
                      <p className="text-[8px] text-primary font-bold uppercase mb-1">{src.type} Context</p>
                      <p className="text-[10px] text-white font-bold">{src.title}</p>
                      {src.snippet && <p className="text-[9px] text-on-surface-variant mt-1 line-clamp-2">{src.snippet}</p>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
             <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center border border-primary/20">
              <span className="material-symbols-outlined text-primary text-sm animate-spin">autorenew</span>
            </div>
            <div className="bg-surface-container rounded-lg rounded-tl-none p-3 border border-white/5">
              <p className="text-xs text-on-surface-variant animate-pulse">Running inference...</p>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-white/5 bg-background/50">
        <div className="relative group focus-within:ring-1 ring-primary rounded-lg">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !loading && handleSend()}
            placeholder="Ask AI Analyst..." 
            disabled={loading}
            className="w-full bg-surface-container border-none focus:ring-0 rounded-lg text-sm py-3 pl-4 pr-12 text-on-surface placeholder-on-surface-variant/50 outline-none"
          />
          <button 
            onClick={handleSend} 
            disabled={loading}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-primary hover:scale-110 transition-transform disabled:opacity-50"
          >
            <span className="material-symbols-outlined">send</span>
          </button>
        </div>
      </div>
    </aside>
  );
}