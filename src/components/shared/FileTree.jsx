import { Download, FileText, Folder, FolderOpen } from 'lucide-react';

export default function FileTree({ items, expandedFolders, onToggleFolder, level = 0 }) {
  return items.map((item, index) => (
    <div key={index} style={{ marginLeft: level * 20 }}>
      {item.type === 'folder' ? (
        <div>
          <div
            className="flex items-center gap-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer rounded"
            onClick={() => onToggleFolder(item.name)}
          >
            {expandedFolders.has(item.name) ? (
              <FolderOpen size={16} className="text-blue-500" />
            ) : (
              <Folder size={16} className="text-blue-500" />
            )}
            <span className="text-sm font-medium">{item.name}</span>
          </div>
          {expandedFolders.has(item.name) && item.children && (
            <div>
              <FileTree
                items={item.children}
                expandedFolders={expandedFolders}
                onToggleFolder={onToggleFolder}
                level={level + 1}
              />
            </div>
          )}
        </div>
      ) : (
        <div className="flex items-center justify-between p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded">
          <div className="flex items-center gap-2">
            <FileText size={16} className="text-gray-500" />
            <span className="text-sm">{item.name}</span>
          </div>
          <a
            href={item.url}
            className="flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded hover:bg-blue-200 dark:hover:bg-blue-800"
          >
            <Download size={12} />
            Download
          </a>
        </div>
      )}
    </div>
  ));
}
