import { initialAgents, mockTasks, artifactsData, initialChatMessages, initialLogs } from '../data/mockData';

const MOCK_API_DELAY = 500;

export const fetchAgents = () => {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve(initialAgents());
    }, MOCK_API_DELAY);
  });
};

export const fetchTasks = () => {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve(mockTasks);
    }, MOCK_API_DELAY);
  });
};

export const fetchArtifacts = () => {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve(artifactsData);
    }, MOCK_API_DELAY);
  });
};

export const fetchMessages = () => {
    return new Promise(resolve => {
      setTimeout(() => {
        resolve(initialChatMessages);
      }, MOCK_API_DELAY);
    });
  };

export const fetchLogs = () => {
    return new Promise(resolve => {
        setTimeout(() => {
            resolve(initialLogs);
        }, MOCK_API_DELAY);
    });
};

export const connectToSSE = (onMessage) => {
  const eventSource = {
    close: () => {
      clearInterval(interval);
    }
  };

  const interval = setInterval(() => {
    const newMessage = {
      id: Date.now(),
      text: `New message from SSE at ${new Date().toLocaleTimeString()}`,
      type: 'system',
    };
    onMessage({ data: JSON.stringify(newMessage) });
  }, 5000);

  return eventSource;
};
