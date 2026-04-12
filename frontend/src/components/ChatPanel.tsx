import { useState } from 'react';
import { ChatMessage } from '../types';

export default function ChatPanel() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      role: "bot",
      content: "Hello! I'm connected to the BetWise Engine. Ask me anything."
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
      setMessages(prev => [...prev, { id: Date.now().toString(), role: "bot", content: "Error connecting to the engine." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-1/3 h-screen bg-white border-l flex flex-col">
      <div className="p-4 border-b bg-gray-50 flex justify-between items-center">
        <h2 className="text-xl font-bold">BetWise Assistant</h2>
        {loading && <span className="text-xs text-blue-500 font-bold animate-pulse">Thinking...</span>}
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.map(msg => (
          <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`p-3 rounded-lg max-w-[85%] ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
              {msg.content}
            </div>
            {msg.sources && msg.sources.map((src, idx) => (
              <div key={idx} className="mt-2 text-xs bg-yellow-50 border border-yellow-200 p-2 rounded w-full max-w-[85%]">
                <span className="font-bold">{src.title || src.type}</span>: {src.snippet || src.value}
              </div>
            ))}
          </div>
        ))}
      </div>

      <div className="p-4 border-t flex gap-2">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !loading && handleSend()}
          placeholder="Ask about the match..." 
          disabled={loading}
          className="flex-1 border rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        />
        <button 
          onClick={handleSend} 
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded font-bold hover:bg-blue-700 disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}