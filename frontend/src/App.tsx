import { useEffect, useState } from 'react'

function App() {
  const [apiStatus, setApiStatus] = useState<string>('Loading...')

  useEffect(() => {
    fetch('http://localhost:8000/')
      .then(res => res.json())
      .then(data => setApiStatus(data.message))
      .catch(() => setApiStatus('API Offline'))
  }, [])

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>BetWise Dashboard</h1>
      <p>Status: {apiStatus}</p>
    </div>
  )
}

export default App