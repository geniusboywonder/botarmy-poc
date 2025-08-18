import React from 'react';
import AgentPanel from '../AgentPanel';
import ActionQueue from '../ActionQueue';
import ProjectViewer from '../ProjectViewer';
import RealtimeLog from '../shared/RealtimeLog';

const Dashboard = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
      <div className="lg:col-span-1 flex flex-col gap-6">
        <AgentPanel />
        <ActionQueue />
      </div>
      <div className="lg:col-span-2">
        <RealtimeLog />
      </div>
      <div className="lg:col-span-3">
        <ProjectViewer />
      </div>
    </div>
  );
};

export default Dashboard;
