import { Circle, ChevronRight, ChevronLeft } from 'lucide-react';
import { getStatusColor } from '../../utils/helpers.js';

export default function Header({ darkMode, setDarkMode, sidebarCollapsed, setSidebarCollapsed, agents }) {
  return (
    <header className="bg-gradient-to-r from-slate-800 to-slate-900 text-white p-4 shadow-lg flex items-center justify-between">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
          Agent Manager
        </h1>
        <div className="flex gap-3 text-sm opacity-90">
          <span className="flex items-center gap-1">
            <Circle
              className={`w-3 h-3 fill-current ${getStatusColor(agents.some(a => a.status === 'error') ? 'error' : 'working')}`}
            />
            {agents.some(a => a.status === 'error') ? 'Errors' : 'Running'}
          </span>
          <span>
            Active: {agents.filter(a => a.status === 'working').length}/10
          </span>
          <span>
            Queue: {agents.reduce((sum, a) => sum + a.queue.todo + a.queue.inProgress, 0)}
          </span>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="p-1.5 rounded hover:bg-white/20"
        >
          {sidebarCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="px-3 py-1 rounded bg-white/20 text-sm"
        >
          {darkMode ? '◐' : '◑'}
        </button>
      </div>
    </header>
  );
}
