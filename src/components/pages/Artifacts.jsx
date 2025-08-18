import { Terminal, BookOpen } from 'lucide-react';
import { artifactTabs } from '../../data/constants.js';
import { artifactsData } from '../../data/mockData.js';
import ArtifactTable from '../shared/ArtifactTable.jsx';
import FileTree from '../shared/FileTree.jsx';

export default function Artifacts({ activeArtifactTab, setActiveArtifactTab, expandedFolders, toggleFolder }) {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-700 to-slate-900 dark:from-slate-100 dark:to-slate-300">
        Artifacts
      </h2>

      {/* Tab Navigation */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <div className="flex overflow-x-auto">
            {artifactTabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveArtifactTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap ${
                  activeArtifactTab === tab.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                <tab.icon size={16} />
                {tab.name}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {/* Development Tab - Tree View */}
          {activeArtifactTab === 'development' && (
            <div className="space-y-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Navigate through the generated source code and documentation
              </p>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
                    <Terminal size={16} />
                    Source Code
                  </h4>
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 max-h-80 overflow-y-auto">
                    <FileTree
                      items={artifactsData.development.source_code}
                      expandedFolders={expandedFolders}
                      onToggleFolder={toggleFolder}
                    />
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
                    <BookOpen size={16} />
                    Documentation
                  </h4>
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 max-h-80 overflow-y-auto">
                    <FileTree
                      items={artifactsData.development.documentation}
                      expandedFolders={expandedFolders}
                      onToggleFolder={toggleFolder}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Other Tabs - Table View */}
          {activeArtifactTab !== 'development' && (
            <ArtifactTable
              artifacts={artifactsData[activeArtifactTab]}
              tabType={activeArtifactTab}
            />
          )}
        </div>
      </div>
    </div>
  );
}
