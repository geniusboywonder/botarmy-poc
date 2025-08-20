import React, { useContext, useState } from 'react';
import { AppContext } from '../context/AppContext.jsx';
import AgentCard from './shared/AgentCard.jsx';

const AgentPanel = () => {
  const { agents, setAgents, loading, error, refetch } = useContext(AppContext);

  const handleToggleExpand = (agentId) => {
    setAgents(
      agents.map((agent) =>
        agent.id === agentId ? { ...agent, expanded: !agent.expanded } : agent
      )
    );
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-4 h-full flex flex-col" data-testid="agent-panel">
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
        <div className="space-y-4 overflow-y-auto">
          {Array.isArray(agents) && agents.length > 0 ? (
            agents.map(agent => (
              <AgentCard
                key={agent.id}
                agent={agent}
                onToggleExpand={handleToggleExpand}
              />
            ))
          ) : (
            <p className="text-gray-500 dark:text-gray-400">No agents available.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default AgentPanel;
