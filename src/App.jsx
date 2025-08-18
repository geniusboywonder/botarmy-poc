import { useState, useContext } from 'react';
import Header from './components/layout/Header.jsx';
import Sidebar from './components/layout/Sidebar.jsx';
import Dashboard from './components/pages/Dashboard.jsx';
import Tasks from './components/pages/Tasks.jsx';
import Logs from './components/pages/Logs.jsx';
import Artifacts from './components/pages/Artifacts.jsx';
import Settings from './components/pages/Settings.jsx';
import StatusBar from './components/StatusBar.jsx';
import { AppContext } from './context/AppContext.js';


export default function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [darkMode, setDarkMode] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const {
    agents,
    logs,
    artifacts,
    logsEndRef
  } = useContext(AppContext);


  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return (
          <Dashboard />
        );
      case 'tasks':
        return <Tasks />;
      case 'logs':
        return <Logs logs={logs} logsEndRef={logsEndRef} />;
      case 'artifacts':
        return (
          <Artifacts
            artifacts={artifacts}
          />
        );
      case 'settings':
        return <Settings agents={agents} />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className={`flex flex-col h-screen ${darkMode ? 'dark' : ''}`}>
      <div className="bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white transition-colors duration-300 flex flex-col flex-1">
        <Header
          darkMode={darkMode}
          setDarkMode={setDarkMode}
          sidebarCollapsed={sidebarCollapsed}
          setSidebarCollapsed={setSidebarCollapsed}
          agents={agents}
        />

        <div className="flex flex-1 overflow-hidden">
          <Sidebar
            activePage={activePage}
            setActivePage={setActivePage}
            sidebarCollapsed={sidebarCollapsed}
          />

          <main className="flex-1 p-6 overflow-y-auto">
            {renderPage()}
          </main>
        </div>
        <StatusBar />
      </div>
    </div>
  );
}
