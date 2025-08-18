export const getStatusColor = (status) => {
  switch (status) {
    case 'working':
      return 'bg-emerald-500';
    case 'error':
      return 'bg-red-500';
    default:
      return 'bg-gray-400';
  }
};

export const getRoleColor = (role) => {
  switch (role) {
    case 'Researcher':
      return 'text-blue-600 dark:text-blue-400';
    case 'Writer':
      return 'text-purple-600 dark:text-purple-400';
    default:
      return 'text-amber-600 dark:text-amber-400';
  }
};
