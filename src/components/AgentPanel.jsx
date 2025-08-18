import React, { useContext } from 'react';
import { AppContext } from '../context/AppContext';

const AgentPanel = () => {
  const { agents } = useContext(AppContext);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-4">
      <h3 className="text-lg font-semibold mb-4">Agents</h3>
      <div className="space-y-4">
        {agents.map(agent => (
          <div key={agent.id} className="p-2 border rounded border-gray-300 dark:border-gray-600">
            <p className="font-bold">{agent.role}</p>
            <p>Status: {agent.status}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AgentPanel;
