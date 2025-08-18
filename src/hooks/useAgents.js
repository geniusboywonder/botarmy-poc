import { useState, useEffect, useRef } from 'react';
import { initialAgents } from '../data/mockData.js';

export function useAgents(projectId, setChatMessages, setLogs) {
  const [agents, setAgents] = useState(initialAgents());
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // With the current environment issues, we'll use mock data to drive the UI.
    // The real SSE connection logic can be re-integrated later.
    const interval = setInterval(() => {
      setAgents(prevAgents => {
        return prevAgents.map(agent => {
          if (Math.random() > 0.7) {
            const newStatus = ['working', 'thinking', 'idle'][Math.floor(Math.random() * 3)];
            return { ...agent, status: newStatus };
          }
          return agent;
        });
      });
       setChatMessages(prev => [...prev, {id: Date.now(), text: 'Simulated agent activity.', type: 'system'}].slice(-8));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const toggleAgentExpand = (agentId) => {
    setAgents(prevAgents =>
      prevAgents.map(agent =>
        agent.id === agentId ? { ...agent, expanded: !agent.expanded } : agent
      )
    );
  };

  return { agents, connected, toggleAgentExpand };
}
