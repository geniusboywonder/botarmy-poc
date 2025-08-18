const handleResponse = async (response) => {
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Something went wrong');
    }
    return response.json();
  };

  export const fetchAgents = async () => {
    const response = await fetch('/api/agents');
    return handleResponse(response);
  };

  export const fetchTasks = async () => {
    const response = await fetch('/api/tasks');
    return handleResponse(response);
  };

  export const fetchArtifacts = async () => {
    const response = await fetch('/api/artifacts');
    return handleResponse(response);
  };

  export const fetchMessages = async () => {
    const response = await fetch('/api/messages');
    return handleResponse(response);
  };

  export const fetchLogs = async () => {
    const response = await fetch('/api/logs');
    return handleResponse(response);
  };

export const connectToSSE = (onMessage) => {
  const eventSource = new EventSource('/api/events');

  eventSource.onmessage = (event) => {
    onMessage(event);
  };

  eventSource.onerror = (err) => {
    console.error('EventSource failed:', err);
    eventSource.close();
  };

  return eventSource;
};
