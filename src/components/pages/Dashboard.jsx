import React from 'react';
import AgentPanel from '../AgentPanel';
import ActionQueue from '../ActionQueue';
import ProjectViewer from '../ProjectViewer';

const Dashboard = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
      <div className="lg:col-span-1">
        <AgentPanel />
      </div>
      <div className="lg:col-span-1">
        <ActionQueue />
      </div>
      <div className="lg:col-span-1">
        <ProjectViewer />
      </div>
    </div>
  );
};

export default Dashboard;
