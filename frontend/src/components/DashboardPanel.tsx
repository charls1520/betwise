export default function DashboardPanel() {
  return (
    <div className="w-2/3 h-screen p-6 overflow-y-auto">
      <h2 className="text-2xl font-bold mb-4">Match Context</h2>
      <div className="bg-white p-4 rounded shadow">
        <h3 className="text-lg font-semibold">Arsenal vs Chelsea</h3>
        <p className="text-gray-600">Premier League - Matchday 30</p>
        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="bg-blue-50 p-3 rounded text-center">
            <span className="block text-sm text-gray-500">Home Win</span>
            <span className="block text-xl font-bold">2.10</span>
          </div>
          <div className="bg-gray-50 p-3 rounded text-center">
            <span className="block text-sm text-gray-500">Draw</span>
            <span className="block text-xl font-bold">3.40</span>
          </div>
          <div className="bg-red-50 p-3 rounded text-center">
            <span className="block text-sm text-gray-500">Away Win</span>
            <span className="block text-xl font-bold">3.60</span>
          </div>
        </div>
      </div>
    </div>
  );
}