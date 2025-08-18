import { Circle, Clock, AlertCircle, CheckCircle } from 'lucide-react';
import { getStatusColor, getRoleColor } from '../../utils/helpers.js';

export default function AgentCard({ agent, onToggleExpand, variant = 'dashboard' }) {
  return (
    <div
      className="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-5 hover:shadow-lg transition"
      onClick={variant === 'dashboard' ? () => onToggleExpand(agent.id) : undefined}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">Agent {agent.id}</h3>
        <div className="flex items-center gap-2">
          <span className={`${getRoleColor(agent.role)} text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700`}>
            {agent.role}
          </span>
          {variant === 'dashboard' && (
            <Circle className={`w-3 h-3 fill-current ${getStatusColor(agent.status)}`} />
          )}
        </div>
      </div>

      {/* Dashboard variant content */}
      {variant === 'dashboard' && (
        <>
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-3 capitalize">
            {agent.status === 'working' && (
              <>
                <Clock size={14} className="inline mr-1 text-emerald-500" /> Working
              </>
            )}
            {agent.status === 'error' && (
              <>
                <AlertCircle size={14} className="inline mr-1 text-red-500" /> Error
              </>
            )}
            {agent.status === 'idle' && 'Idle'}
          </div>
          <div className="text-xs text-gray-500 mb-3">
            Queue: {agent.queue.todo} todo, {agent.queue.inProgress} in progress
          </div>
          {agent.currentTask && (
            <div className="mb-3 p-2 bg-gray-50 dark:bg-gray-700/50 rounded text-xs truncate">
              <span className="font-medium">Task:</span> {agent.currentTask}
            </div>
          )}
          {agent.handoff && (
            <div className="text-xs text-amber-600 dark:text-amber-400">
              🔄 Handing to {agent.handoff}
            </div>
          )}
          {agent.expanded && (
            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700 text-xs">
              <div className="font-mono text-gray-600 dark:text-gray-400 space-y-1 h-16 overflow-y-auto">
                {agent.chat.length ? (
                  agent.chat.map((msg, i) => <div key={i}>• {msg}</div>)
                ) : (
                  <div className="text-gray-400">No history</div>
                )}
              </div>
              <div className="mt-2 text-gray-500 dark:text-gray-400">
                Done: {agent.queue.done} | Failed: {agent.queue.failed}
              </div>
            </div>
          )}
        </>
      )}

      {/* Settings variant content */}
      {variant === 'settings' && (
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Role Configuration File
            </label>
            <input
              type="file"
              accept=".json,.md"
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded text-sm dark:bg-gray-700 dark:text-gray-300 file:mr-3 file:py-1 file:px-2 file:rounded file:border-0 file:text-xs file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>

          {agent.id <= 2 && (
            <div className="text-xs text-green-600 dark:text-green-400 flex items-center gap-1">
              <CheckCircle size={12} />
              Uploaded: role_agent{agent.id}.json
            </div>
          )}

          {agent.id > 2 && (
            <div className="text-xs text-gray-500 dark:text-gray-400">
              No configuration file uploaded
            </div>
          )}
        </div>
      )}
    </div>
  );
}
