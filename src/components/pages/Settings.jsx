import { systemConfigFields } from '../../data/mockData.js';
import AgentCard from '../shared/AgentCard.jsx';

export default function Settings({ agents }) {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-700 to-slate-900 dark:from-slate-100 dark:to-slate-300">
        Settings
      </h2>

      {/* Agent Role Files Grid */}
      <div>
        <h3 className="text-xl font-semibold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-slate-700 to-slate-900 dark:from-slate-100 dark:to-slate-300">
          Agent Role Configuration
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map(agent => (
            <AgentCard
              key={agent.id}
              agent={agent}
              variant="settings"
            />
          ))}
        </div>
      </div>

      {/* System Configuration */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6 border border-gray-200 dark:border-gray-700 space-y-6">
        <h3 className="text-xl font-semibold bg-clip-text text-transparent bg-gradient-to-r from-slate-700 to-slate-900 dark:from-slate-100 dark:to-slate-300">
          System Configuration
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {systemConfigFields.map((field, i) => (
            <div key={i}>
              <label className="block text-sm font-medium mb-1">
                {field.label}
              </label>
              <input
                type="text"
                defaultValue={field.value}
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded dark:bg-gray-700"
              />
            </div>
          ))}
        </div>

        <button className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded hover:from-blue-700 hover:to-purple-700">
          Save Settings
        </button>
      </div>
    </div>
  );
}
