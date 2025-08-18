import React, { useContext, useState } from 'react';
import { AppContext } from '../context/AppContext.jsx';
import { ChevronRight, Folder, File } from 'lucide-react';

const FileTree = ({ files }) => {
  if (!files) return null;

  return (
    <ul className="pl-4">
      {Object.entries(files).map(([name, content]) => {
        if (Array.isArray(content)) {
          return content.map((item, index) => (
            <li key={index} className="flex items-center">
              <File size={16} className="mr-2" />
              {item.name}
            </li>
          ));
        }
        if (typeof content === 'object') {
          return (
            <li key={name}>
              <div className="flex items-center">
                <Folder size={16} className="mr-2" />
                {name}
              </div>
              <FileTree files={content} />
            </li>
          );
        }
        return null;
      })}
    </ul>
  );
};

const ProjectViewer = () => {
  const { artifacts, loading, error, refetch } = useContext(AppContext);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-4">
      <h3 className="text-lg font-semibold mb-4">Project Viewer</h3>
      {loading.artifacts && <p>Loading artifacts...</p>}
      {error.artifacts && (
        <div>
          <p className="text-red-500" data-testid="error-message">{error.artifacts}</p>
          <button onClick={() => refetch('artifacts')} className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Retry
          </button>
        </div>
      )}
      {!loading.artifacts && !error.artifacts && <FileTree files={artifacts} />}
    </div>
  );
};

export default ProjectViewer;
