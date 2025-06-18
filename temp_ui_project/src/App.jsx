import React, { useEffect, useState } from 'react';
import AnalysisForm from './components/AnalysisForm';
import AnalysisResults from './components/AnalysisResults';

function App() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysisId, setAnalysisId] = useState(null);
  const [userId, setUserId] = useState(localStorage.getItem('userId') || '');
  const [showLogin, setShowLogin] = useState(!userId);

  useEffect(() => {
    fetch('http://localhost:5000/api/business-metrics')
      .then(res => res.json())
      .then(data => {
        setMetrics(data);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to fetch metrics');
        setLoading(false);
      });
  }, []);

  const handleLogin = (e) => {
    e.preventDefault();
    if (userId) {
      localStorage.setItem('userId', userId);
      setShowLogin(false);
    }
  };

  const handleLogout = () => {
    setUserId('');
    localStorage.removeItem('userId');
    setShowLogin(true);
  };

  if (showLogin) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
        <form onSubmit={handleLogin} className="bg-white rounded shadow p-6 w-full max-w-xs">
          <h2 className="text-xl font-bold mb-4">Sign In</h2>
          <input
            type="text"
            value={userId}
            onChange={e => setUserId(e.target.value)}
            placeholder="Enter your user ID"
            className="border rounded p-2 w-full mb-4"
            required
          />
          <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded w-full">Sign In</button>
        </form>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-8">
      <div className="w-full max-w-md flex justify-between items-center mb-4">
        <h1 className="text-3xl font-bold">B2BValue GTM Dashboard</h1>
        <button onClick={handleLogout} className="text-blue-600 underline ml-4">Logout</button>
      </div>
      {loading && <p>Loading business metrics...</p>}
      {error && <p className="text-red-500">{error}</p>}
      {metrics && (
        <div className="bg-white rounded shadow p-6 w-full max-w-md mb-8">
          <h2 className="text-xl font-semibold mb-4">Business Metrics</h2>
          <ul className="space-y-2">
            <li><strong>ROI:</strong> {metrics.roi}</li>
            <li><strong>Payback Period:</strong> {metrics.payback_period} months</li>
            <li><strong>NPV:</strong> ${metrics.npv}</li>
          </ul>
        </div>
      )}
      {!analysisId && <AnalysisForm onAnalysisStarted={setAnalysisId} />}
      {analysisId && <AnalysisResults analysisId={analysisId} onBack={() => setAnalysisId(null)} />}
    </div>
  );
}

export default App;
