import { useState } from 'react';
import { ChatMessage } from '../types';

export default function ChatPanel() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      role: "bot",
      content: "Hello! I'm ready to analyze the Arsenal vs Chelsea match. What would you like to know?"
    }
  ]);

  const handleSend = () => {
    if (!input.trim()) return;
    
    const userMsg: ChatMessage = { id: Date.now().toString(), role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");

    // Mock bot response
    setTimeout(() => {
      const botMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "bot",
        content: "Based on recent news, Arsenal's star striker is out with a knee injury. This might affect the Over 2.5 goals line.",
        sources: [
          { type: "news", title: "BBC Sport", snippet: "Knee injury sidelines striker for 3 weeks..." }
        ]
      };
      setMessages(prev => [...prev, botMsg]);
    }, 1000);
  };

  return (
    <div className="w-1/3 h-screen bg-white border-l flex flex-col">
      <div className="p-4 border-b bg-gray-50">
        <h2 className="text-xl font-bold">BetWise Assistant</h2>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.map(msg => (
          <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`p-3 rounded-lg max-w-[85%] ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
              {msg.content}
            </div>
            {msg.sources && msg.sources.map((src, idx) => (
              <div key={idx} className="mt-2 text-xs bg-yellow-50 border border-yellow-200 p-2 rounded w-full max-w-[85%]">
                <span className="font-bold">{src.title || src.market}</span>: {src.snippet || src.value}
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
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask about the match..." 
          className="flex-1 border rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button onClick={handleSend} className="bg-blue-600 text-white px-4 py-2 rounded font-bold hover:bg-blue-700">
          Send
        </button>
      </div>
    </div>
  );
}