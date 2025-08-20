import React, { useContext, useState } from 'react';
import { AppContext } from '../context/AppContext.jsx';
import { ChevronRight, Folder, File, FolderOpen } from 'lucide-react';

const transformArtifactsToTree = (artifacts) => {
  if (!artifacts || typeof artifacts !== 'object') {
    return [];
  }

  return Object.entries(artifacts).map(([name, content]) => {
    if (Array.isArray(content)) {
      return {
        name,
        children: content.map(item => ({ name: item.name || item }))
      };
    }
    if (typeof content === 'object' && content !== null) {
      return {
        name,
        children: transformArtifactsToTree(content)
      };
    }
    return { name };
  });
};

const FileTreeItem = ({ node }) => {
  const [isOpen, setIsOpen] = useState(true);
  const hasChildren = node.children && node.children.length > 0;

  return (
    <li>
      <div
        onClick={() => hasChildren && setIsOpen(!isOpen)}
        className={`flex items-center ${hasChildren ? 'cursor-pointer' : ''}`}
        data-testid={`treeitem-${node.name}`}
      >
        {hasChildren ? (
          <>
            <ChevronRight size={16} className={`mr-1 flex-shrink-0 transition-transform ${isOpen ? 'rotate-90' : ''}`} />
            {isOpen ? <FolderOpen size={16} className="mr-2 flex-shrink-0 text-blue-500" /> : <Folder size={16} className="mr-2 flex-shrink-0 text-blue-500" />}
          </>
        ) : (
          <File size={16} className="mr-2 ml-5 flex-shrink-0" />
        )}
        <span className={hasChildren ? "font-medium" : ""}>{node.name}</span>
      </div>
      {hasChildren && isOpen && (
        <ul className="pl-6 border-l border-gray-200 dark:border-gray-700">
          {node.children.map((childNode, index) => (
            <FileTreeItem key={index} node={childNode} />
          ))}
        </ul>
      )}
    </li>
  );
};

const ProjectViewer = () => {
  const { artifacts, loading, error, refetch } = useContext(AppContext);
  const fileTree = transformArtifactsToTree(artifacts);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 p-4">
      <h3 className="text-lg font-semibold mb-4">Project Specification</h3>
      {loading.artifacts && <p>Loading artifacts...</p>}
      {error.artifacts && (
        <div>
          <p className="text-red-500">{error.artifacts}</p>
          <button onClick={() => refetch('artifacts')} className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Retry
          </button>
        </div>
      )}
      {!loading.artifacts && !error.artifacts && (
        fileTree.length > 0 ? (
          <ul className="font-mono text-sm">
            {fileTree.map((node, index) => (
              <FileTreeItem key={index} node={node} />
            ))}
          </ul>
        ) : (
          <p className="text-gray-500 dark:text-gray-400">No project specification generated yet.</p>
        )
      )}
    </div>
  );
};

export default ProjectViewer;
