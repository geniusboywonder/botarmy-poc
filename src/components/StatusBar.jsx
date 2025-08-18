import React, { useContext } from 'react';
import { AppContext } from '../context/AppContext.jsx';
import { Users, ListChecks, Wifi, WifiOff, AlertTriangle } from 'lucide-react';

const StatusBar = () => {
  const { agents, tasks, error } = useContext(AppContext);

  const idleAgents = agents.filter(a => a.status === 'idle').length;
  const busyAgents = agents.length - idleAgents;
  const queuedTasks = tasks.filter(t => t.status === 'WIP' || t.status === 'Waiting' || t.status === 'To Do').length;

  const hasError = Object.values(error).some(e => e !== null);
  // A simple heuristic for connection status. If there are no agents after initial load, we might be disconnected.
  const isConnected = agents.length > 0 || !Object.values(error).some(e => e);

  const getStatus = () => {
    if (hasError) {
      return (
        <span className="flex items-center text-red-500">
          <AlertTriangle size={14} className="mr-1" />
          Error
        </span>
      );
    }
    if (isConnected) {
      return (
        <span className="flex items-center text-green-500">
          <Wifi size={14} className="mr-1" />
          Connected
        </span>
      );
    }
    return (
      <span className="flex items-center text-yellow-500">
        <WifiOff size={14} className="mr-1" />
        Connecting...
      </span>
    );
  };

  return (
    <div className="bg-gray-100 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 px-4 py-2 flex justify-between items-center text-sm">
      <div className="flex items-center gap-4">
        <span className="flex items-center">
          <Users size={14} className="mr-1" />
          Agents: {idleAgents} idle, {busyAgents} busy
        </span>
        <span className="flex items-center">
          <ListChecks size={14} className="mr-1" />
          Tasks in Queue: {queuedTasks}
        </span>
      </div>
      <div>
        {getStatus()}
      </div>
    </div>
  );
};

export default StatusBar;
