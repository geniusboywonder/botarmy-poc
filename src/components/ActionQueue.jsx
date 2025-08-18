import React, { useContext } from 'react';
import { AppContext } from '../context/AppContext';

const ActionQueue = () => {
  const { tasks, loading, error } = useContext(AppContext);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-4">
      <h3 className="text-lg font-semibold mb-4">Action Queue</h3>
      {loading.tasks && <p>Loading tasks...</p>}
      {error.tasks && <p className="text-red-500" data-testid="error-message">{error.tasks}</p>}
      {!loading.tasks && !error.tasks && (
        <div className="space-y-2">
          {tasks.map((task, index) => (
            <div key={index} className="p-2 border rounded border-gray-300 dark:border-gray-600">
              <p className="font-bold">{task.name}</p>
              <p>Status: {task.status}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ActionQueue;
