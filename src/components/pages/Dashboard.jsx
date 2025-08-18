import { Send, AlertCircle, CheckCircle, User, FileText } from 'lucide-react';
import AgentCard from '../shared/AgentCard.jsx';

export default function Dashboard({ agents, chatMessages, chatEndRef, setChatMessages, toggleAgentExpand }) {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-700 to-slate-900 dark:from-slate-100 dark:to-slate-300">
        Dashboard
      </h2>

      {/* Chat */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 h-60 flex flex-col">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex-1 overflow-y-auto space-y-2">
          {chatMessages.slice(-8).map((msg, i) => (
            <div
              key={i}
              className={`flex items-center gap-2 text-sm ${
                msg.type === 'error'
                  ? 'text-red-600 dark:text-red-400'
                  : msg.type === 'success'
                    ? 'text-emerald-600 dark:text-emerald-400'
                    : msg.type === 'handoff'
                      ? 'text-amber-600 dark:text-amber-400'
                      : 'text-gray-700 dark:text-gray-300'
              }`}
            >
              {msg.type === 'error' && <AlertCircle size={14} />}
              {msg.type === 'success' && <CheckCircle size={14} />}
              {msg.type === 'handoff' && <User size={14} />}
              {msg.type === 'system' && <FileText size={14} />}
              <span className="font-mono">• {msg.text}</span>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex gap-2">
          <input
            type="text"
            placeholder="Send instruction..."
            className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700"
            onKeyPress={e => {
              if (e.key === 'Enter' && e.target.value) {
                setChatMessages(m => [...m, {
                  id: Date.now(),
                  text: `You: ${e.target.value}`,
                  type: 'user',
                }]);
                e.target.value = '';
              }
            }}
          />
          <button className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded hover:from-blue-700 hover:to-purple-700">
            <Send size={18} />
          </button>
        </div>
      </div>

      {/* Agents Grid */}
      <div>
        <h3 className="text-xl font-semibold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-slate-700 to-slate-900 dark:from-slate-100 dark:to-slate-300">
          Agents
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map(agent => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onToggleExpand={toggleAgentExpand}
              variant="dashboard"
            />
          ))}
        </div>
      </div>
    </div>
  );
}
