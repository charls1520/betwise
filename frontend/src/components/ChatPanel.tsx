export default function ChatPanel() {
  return (
    <div className="w-1/3 h-screen bg-white border-l flex flex-col">
      <div className="p-4 border-b bg-gray-50">
        <h2 className="text-xl font-bold">BetWise Assistant</h2>
      </div>
      <div className="flex-1 p-4 overflow-y-auto">
        <p className="text-gray-500 text-center mt-10">Chat interface coming soon...</p>
      </div>
      <div className="p-4 border-t">
        <input 
          type="text" 
          placeholder="Ask about the match..." 
          className="w-full border rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  );
}