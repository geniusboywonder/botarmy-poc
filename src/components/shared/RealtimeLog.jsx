import React, { useContext, useEffect, useRef } from 'react';
import { AppContext } from '../../context/AppContext';

const RealtimeLog = () => {
  const { chatMessages, logs } = useContext(AppContext);
  const logContainerRef = useRef(null);

  // Combine and sort messages and logs by timestamp
  const combinedFeed = [...chatMessages, ...logs].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [combinedFeed]);

  const renderItem = (item) => {
    if (item.from_agent) { // It's a chat message
      return (
        <div key={item.id} className="p-2 rounded bg-gray-100 dark:bg-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400">{item.from_agent} to {item.to_agent}</p>
          <p className="font-mono text-sm">{item.content.requirements || JSON.stringify(item.content)}</p>
        </div>
      );
    } else { // It's a log
      return (
        <div key={item.id} className="p-2">
          <p className="font-mono text-xs text-green-500">{`> ${item.message}`}</p>
        </div>
      );
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-4 h-full flex flex-col">
      <h3 className="text-lg font-semibold mb-4">Real-time Feed</h3>
      <div ref={logContainerRef} className="flex-1 overflow-y-auto space-y-2">
        {combinedFeed.map(renderItem)}
      </div>
    </div>
  );
};

export default RealtimeLog;
