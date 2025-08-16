                        >
                          Download
                        </button>
                      </div>
                    </div>
                    
                    {/* File preview/content */}
                    <div className="mt-3">
                      <pre className="bg-gray-50 rounded p-3 text-sm overflow-x-auto max-h-48">
                        <code>{file.content.substring(0, 500)}{file.content.length > 500 ? '...' : ''}</code>
                      </pre>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default ProjectViewer;'''

    def _generate_status_bar(self) -> str:
        """Generate StatusBar component."""
        
        return '''import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import apiClient from '../utils/api';

function StatusBar() {
  const { state } = useApp();
  const [systemStatus, setSystemStatus] = useState(null);
  const [usageStats, setUsageStats] = useState(null);
  
  useEffect(() => {
    // Fetch system status periodically
    const fetchSystemStatus = async () => {
      try {
        const status = await apiClient.getSystemStatus();
        setSystemStatus(status);
      } catch (error) {
        console.error('Failed to fetch system status:', error);
      }
    };

    const fetchUsageStats = async () => {
      try {
        const stats = await apiClient.getUsageStats();
        setUsageStats(stats);
      } catch (error) {
        console.error('Failed to fetch usage stats:', error);
      }
    };

    fetchSystemStatus();
    fetchUsageStats();

    // Update every 30 seconds
    const interval = setInterval(() => {
      fetchSystemStatus();
      fetchUsageStats();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const getConnectionStatus = () => {
    if (state.connected) {
      return { status: 'connected', color: 'text-green-600', label: 'Connected' };
    }
    return { status: 'disconnected', color: 'text-red-600', label: 'Disconnected' };
  };

  const connection = getConnectionStatus();

  return (
    <div className="bg-white border-t border-gray-200 px-6 py-3">
      <div className="flex items-center justify-between">
        {/* Left side - System status */}
        <div className="flex items-center space-x-6">
          {/* Connection status */}
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${connection.status === 'connected' ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className={`text-sm font-medium ${connection.color}`}>
              {connection.label}
            </span>
          </div>

          {/* System health */}
          {systemStatus && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">System:</span>
              <span className={`text-sm font-medium ${
                systemStatus.status === 'healthy' ? 'text-green-600' : 'text-yellow-600'
              }`}>
                {systemStatus.status}
              </span>
            </div>
          )}

          {/* Current project status */}
          {state.project.id && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Project:</span>
              <span className="text-sm font-medium text-blue-600">
                {state.project.status}
              </span>
            </div>
          )}
        </div>

        {/* Right side - Usage stats and performance */}
        <div className="flex items-center space-x-6">
          {/* API usage */}
          {usageStats && (
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                <span className="font-medium">{usageStats.total_requests}</span> requests
              </div>
              <div className="text-sm text-gray-600">
                <span className="font-medium">{usageStats.total_tokens.toLocaleString()}</span> tokens
              </div>
              <div className="text-sm text-gray-600">
                $<span className="font-medium">{usageStats.total_cost}</span> cost
              </div>
            </div>
          )}

          {/* Loading indicator */}
          {state.loading && (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-indigo-500 border-t-transparent" />
              <span className="text-sm text-gray-600">Processing...</span>
            </div>
          )}

          {/* Error indicator */}
          {state.error && (
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-red-500" />
              <span className="text-sm text-red-600">Error</span>
            </div>
          )}

          {/* Active agents count */}
          <div className="text-sm text-gray-600">
            <span className="font-medium">
              {Object.values(state.agents).filter(agent => agent.status === 'processing').length}
            </span> active agents
          </div>
        </div>
      </div>
    </div>
  );
}

export default StatusBar;'''

    def generate_package_json(self) -> str:
        """Generate package.json for React app."""
        
        return '''{
  "name": "botarmy-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@vitejs/plugin-react": "^4.1.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.31",
    "tailwindcss": "^3.3.5",
    "vite": "^4.5.0"
  }
}'''

    def generate_vite_config(self) -> str:
        """Generate Vite configuration."""
        
        return '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../static',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})'''

    def generate_tailwind_config(self) -> str:
        """Generate Tailwind CSS configuration."""
        
        return '''/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bot-blue': '#3B82F6',
        'bot-indigo': '#6366F1',
        'bot-purple': '#8B5CF6',
        'bot-green': '#10B981',
        'bot-red': '#EF4444',
        'bot-orange': '#F59E0B',
        'bot-gray': {
          50: '#F9FAFB',
          100: '#F3F4F6',
          200: '#E5E7EB',
          300: '#D1D5DB',
          400: '#9CA3AF',
          500: '#6B7280',
          600: '#4B5563',
          700: '#374151',
          800: '#1F2937',
          900: '#111827'
        }
      }
    },
  },
  plugins: [],
}'''

    def generate_index_html(self) -> str:
        """Generate index.html template."""
        
        return '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>BotArmy - AI Agent Development Platform</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>'''

    def generate_main_jsx(self) -> str:
        """Generate main.jsx entry point."""
        
        return '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import { AppProvider } from './context/AppContext.js'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AppProvider>
      <App />
    </AppProvider>
  </React.StrictMode>,
)'''

    def generate_index_css(self) -> str:
        """Generate index.css with Tailwind imports."""
        
        return '''@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html {
    font-family: 'Inter', system-ui, sans-serif;
  }
}

@layer components {
  .btn-primary {
    @apply bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors;
  }

  .btn-secondary {
    @apply bg-gray-100 text-gray-900 px-4 py-2 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors;
  }

  .btn-danger {
    @apply bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors;
  }

  .card {
    @apply bg-white rounded-lg shadow-sm border border-gray-200;
  }

  .input-field {
    @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500;
  }
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}'''
