import { navItems } from '../../data/constants.js';

export default function Sidebar({ activePage, setActivePage, sidebarCollapsed }) {
  return (
    <nav className={`flex-shrink-0 border-r bg-white dark:bg-gray-800 transition-all ${sidebarCollapsed ? 'w-16' : 'w-60'}`}>
      <div className="p-3 space-y-1">
        {navItems.map(item => (
          <div key={item.id} className="group relative">
            <button
              onClick={() => setActivePage(item.id)}
              className={`w-full flex items-center gap-3 p-3 rounded-lg transition-all ${
                activePage === item.id
                  ? 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 font-medium'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <item.icon size={20} />
              {!sidebarCollapsed && <span>{item.name}</span>}
            </button>
            {sidebarCollapsed && (
              <div className="fixed left-16 ml-2 px-2 py-1 bg-gray-800 text-white text-sm rounded pointer-events-none opacity-0 group-hover:opacity-100 z-50 whitespace-nowrap">
                {item.name}
              </div>
            )}
          </div>
        ))}
      </div>
    </nav>
  );
}
