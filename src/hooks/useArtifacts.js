import { useState } from 'react';

export function useArtifacts() {
  const [activeArtifactTab, setActiveArtifactTab] = useState('development');
  const [expandedFolders, setExpandedFolders] = useState(new Set());

  const toggleFolder = (folderPath) => {
    setExpandedFolders(prevExpanded => {
      const newExpanded = new Set(prevExpanded);
      if (newExpanded.has(folderPath)) {
        newExpanded.delete(folderPath);
      } else {
        newExpanded.add(folderPath);
      }
      return newExpanded;
    });
  };

  return {
    activeArtifactTab,
    setActiveArtifactTab,
    expandedFolders,
    toggleFolder,
  };
}
