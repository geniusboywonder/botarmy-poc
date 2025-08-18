import React, { useContext } from 'react';
import { AppContext } from '../context/AppContext.jsx';

const AgentPanel = () => {
  const { agents, loading, error, refetch } = useContext(AppContext);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-4" data-testid="agent-panel">
      <h3 className="text-lg font-semibold mb-4">Agents</h3>
      {loading.agents && <p>Loading agents...</p>}
      {error.agents && (
        <div>
          <p className="text-red-500" data-testid="error-message">{error.agents}</p>
          <button onClick={() => refetch('agents')} className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Retry
          </button>
        </div>
      )}
      {!loading.agents && !error.agents && (
        <div className="space-y-4">
          {agents.map(agent => (
            <div key={agent.id} className="p-2 border rounded border-gray-300 dark:border-gray-600">
              <p className="font-bold">{agent.role}</p>
              <p>Status: {agent.status}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AgentPanel;
