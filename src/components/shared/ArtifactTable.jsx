import { Download } from 'lucide-react';

export default function ArtifactTable({ artifacts, tabType }) {
  const getDescription = (tabType) => {
    const descriptions = {
      requirements: 'Requirements documents and user stories from the Analyst agent',
      design: 'Architecture diagrams and design models from the Architect agent',
      testing: 'Test plans, cases, and scripts from the Testing agent',
      deployment: 'Deployment scripts and configuration files from the Deployment agent',
      maintenance: 'Monitoring reports and logs from the Maintenance agent'
    };
    return descriptions[tabType] || '';
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-600 dark:text-gray-400">
        {getDescription(tabType)}
      </p>

      <div className="overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-750">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-900 dark:text-gray-100">
                Document Name
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-900 dark:text-gray-100">
                Type
              </th>
              <th className="px-4 py-3 text-right text-sm font-medium text-gray-900 dark:text-gray-100">
                Download
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {artifacts?.map((artifact, index) => (
              <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100">
                  {artifact.name}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {artifact.type}
                </td>
                <td className="px-4 py-3 text-right">
                  <a
                    href={artifact.url}
                    className="inline-flex items-center gap-1 px-3 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
                  >
                    <Download size={12} />
                    Download
                  </a>
                </td>
              </tr>
            )) || (
              <tr>
                <td colSpan="3" className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                  No artifacts available yet
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
