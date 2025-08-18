import React, { useContext, useState } from 'react';
import { AppContext } from '../context/AppContext.jsx';
import { respondToAction } from '../utils/api.js';
import { AlertOctagon, Info, ShieldQuestion } from 'lucide-react';

const ActionQueue = () => {
  const { tasks, loading, error, refetch } = useContext(AppContext);
  const [isSubmitting, setIsSubmitting] = useState({ id: null, option: null });

  const handleAction = async (actionId, response) => {
    setIsSubmitting({ id: actionId, option: response });
    try {
      await respondToAction(actionId, response);
      refetch('tasks'); // Refetch tasks to update the queue
    } catch (e) {
      console.error("Failed to respond to action:", e);
      // Optionally, show an error message to the user
    } finally {
      setIsSubmitting({ id: null, option: null });
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'high':
        return <AlertOctagon className="text-red-500" size={20} />;
      case 'medium':
        return <ShieldQuestion className="text-yellow-500" size={20} />;
      default:
        return <Info className="text-blue-500" size={20} />;
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-4 h-full flex flex-col">
      <h3 className="text-lg font-semibold mb-4">Action Queue</h3>
      {loading.tasks && <p>Loading tasks...</p>}
      {error.tasks && (
        <div>
          <p className="text-red-500">{error.tasks}</p>
          <button onClick={() => refetch('tasks')} className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Retry
          </button>
        </div>
      )}
      {!loading.tasks && !error.tasks && (
        <div className="space-y-4 overflow-y-auto">
          {tasks.length === 0 && <p className="text-gray-500 dark:text-gray-400">No pending actions.</p>}
          {tasks.map((task) => (
            <div key={task.id} className="p-4 border rounded-lg border-gray-200 dark:border-gray-700 flex gap-4">
              <div className="flex-shrink-0">{getPriorityIcon(task.priority)}</div>
              <div className="flex-1">
                <p className="font-bold text-gray-800 dark:text-gray-200">{task.title}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{task.description}</p>
                <div className="flex flex-wrap gap-2">
                  {task.options.map((option, index) => {
                    const submitting = isSubmitting.id === task.id && isSubmitting.option === option;
                    return (
                      <button
                        key={index}
                        onClick={() => handleAction(task.id, option)}
                        disabled={isSubmitting.id === task.id}
                        className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50"
                      >
                        {submitting ? 'Submitting...' : option}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ActionQueue;
