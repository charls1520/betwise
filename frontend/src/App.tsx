import DashboardPanel from './components/DashboardPanel';
import ChatPanel from './components/ChatPanel';

function App() {
  return (
    <div className="flex w-full h-screen bg-gray-100">
      <DashboardPanel />
      <ChatPanel />
    </div>
  );
}

export default App;