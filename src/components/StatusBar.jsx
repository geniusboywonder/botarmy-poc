import React, { useContext } from 'react';
import { AppContext } from '../context/AppContext.jsx';

const StatusBar = () => {
  const { agents, tasks } = useContext(AppContext);

  const idleAgents = agents.filter(a => a.status === 'idle').length;
  const busyAgents = agents.length - idleAgents;
  const queuedTasks = tasks.filter(t => t.status === 'WIP' || t.status === 'Waiting' || t.status === 'To Do').length;

  return (
    <div className="bg-gray-100 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 p-2 flex justify-between items-center text-sm">
      <div>
        <span>Agents: {idleAgents} idle, {busyAgents} busy</span>
      </div>
      <div>
        <span>Tasks in Queue: {queuedTasks}</span>
      </div>
      <div>
        <span>Status: All systems operational</span>
      </div>
    </div>
  );
};

export default StatusBar;
