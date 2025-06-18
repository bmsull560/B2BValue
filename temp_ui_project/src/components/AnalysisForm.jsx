import React, { useState } from 'react';

export default function AnalysisForm({ onAnalysisStarted }) {
  const [content, setContent] = useState('');
  const [contentType, setContentType] = useState('text');
  const [creatorId, setCreatorId] = useState('demo-user');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('http://localhost:5000/api/start-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, content_type: contentType, creator_id: creatorId })
      });
      const data = await res.json();
      if (res.ok) {
        onAnalysisStarted(data.id);
      } else {
        setError(data.detail || 'Failed to start analysis');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded shadow p-6 w-full max-w-md mb-8">
      <h2 className="text-xl font-semibold mb-4">Start New Analysis</h2>
      <div className="mb-4">
        <label className="block mb-1 font-medium">Content</label>
        <textarea value={content} onChange={e => setContent(e.target.value)} required className="w-full border rounded p-2" rows={3} />
      </div>
      <div className="mb-4">
        <label className="block mb-1 font-medium">Content Type</label>
        <select value={contentType} onChange={e => setContentType(e.target.value)} className="w-full border rounded p-2">
          <option value="text">Text</option>
          <option value="spreadsheet">Spreadsheet</option>
          <option value="pdf">PDF</option>
        </select>
      </div>
      <div className="mb-4">
        <label className="block mb-1 font-medium">Your User ID</label>
        <input value={creatorId} onChange={e => setCreatorId(e.target.value)} className="w-full border rounded p-2" />
      </div>
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <button type="submit" disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
        {loading ? 'Starting...' : 'Start Analysis'}
      </button>
    </form>
  );
}
