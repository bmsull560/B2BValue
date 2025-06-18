import React, { useEffect, useState } from 'react';

export default function AnalysisResults({ analysisId, onBack }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!analysisId) return;
    setLoading(true);
    fetch(`http://localhost:5000/api/analysis-results/${analysisId}`)
      .then(res => res.json())
      .then(data => {
        setResults(data);
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to fetch results');
        setLoading(false);
      });
  }, [analysisId]);

  if (!analysisId) return null;

  return (
    <div className="bg-white rounded shadow p-6 w-full max-w-md">
      <button onClick={onBack} className="mb-4 text-blue-600 underline">&larr; Back</button>
      <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
      {loading && <p>Loading results...</p>}
      {error && <p className="text-red-500">{error}</p>}
      {results && (
        <div>
          <pre className="bg-gray-100 rounded p-2 text-sm overflow-x-auto">{JSON.stringify(results, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
