import DashboardPanel from './components/DashboardPanel';
import ChatPanel from './components/ChatPanel';

function App() {
  return (
    <div className="flex w-full h-screen bg-background overflow-hidden">
      <DashboardPanel />
      <ChatPanel />
    </div>
  );
}

export default App;