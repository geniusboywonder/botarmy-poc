import { mockTasks } from '../../data/mockData.js';

export default function Tasks() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-700 to-slate-900 dark:from-slate-100 dark:to-slate-300">
        Task Monitor
      </h2>
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden border border-gray-200 dark:border-gray-700">
        <table className="w-full table-auto">
          <thead className="bg-gray-50 dark:bg-gray-750 text-left text-sm">
            <tr>
              <th className="p-4 font-medium">Task Name</th>
              <th>Status</th>
              <th>Agent Role</th>
              <th>Time Taken</th>
              <th>Feedback</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {mockTasks.map((task, i) => (
              <tr key={i} className="border-t hover:bg-gray-50 dark:hover:bg-gray-700/50">
                <td className="p-4 font-medium">{task.name}</td>
                <td>
                  <span
                    className={`px-2 py-1 rounded-full text-xs ${
                      task.status === 'Done'
                        ? 'bg-green-100 text-green-800'
                        : task.status === 'Error'
                          ? 'bg-red-100 text-red-800'
                          : task.status === 'WIP'
                            ? 'bg-blue-100 text-blue-800'
                            : task.status === 'Waiting'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {task.status}
                  </span>
                </td>
                <td className="text-gray-600 dark:text-gray-400">{task.role}</td>
                <td className="text-gray-600 dark:text-gray-400">{task.time}</td>
                <td className="text-gray-600 dark:text-gray-400">{task.feedback}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
