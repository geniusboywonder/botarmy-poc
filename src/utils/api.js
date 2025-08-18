const handleResponse = async (response) => {
  if (!response.ok) {
    const errorText = await response.text();
    try {
      const errorJson = JSON.parse(errorText);
      throw new Error(errorJson.detail || 'Something went wrong');
    } catch (e) {
      throw new Error(errorText || 'Something went wrong');
    }
  }
  return response.json();
};

export const fetchAgents = async (projectId) => {
  if (!projectId) return [];
  // Backend does not have a dedicated agent endpoint, returning mock data
  console.warn("API: fetchAgents is returning mock data.");
  return Promise.resolve([
    {
      id: 'analyst',
      role: 'Analyst',
      status: 'working',
      queue: { todo: 3, inProgress: 1, done: 5, failed: 0 },
      currentTask: 'Analyzing user requirements for project X.',
      handoff: null,
      expanded: false,
      chat: ['Initial analysis started.', 'Found 3 key requirements.'],
    },
    {
      id: 'architect',
      role: 'Architect',
      status: 'idle',
      queue: { todo: 1, inProgress: 0, done: 8, failed: 1 },
      currentTask: null,
      handoff: null,
      expanded: false,
      chat: ['Received analysis from Analyst.', 'Designed initial architecture.'],
    },
  ]);
};

export const fetchTasks = async (projectId) => {
  if (!projectId) return [];
  const response = await fetch(`/api/projects/${projectId}/actions`);
  const data = await handleResponse(response);
  return data.actions; // The endpoint returns { "actions": [...] }
};

export const fetchArtifacts = async (projectId) => {
  if (!projectId) return {};
  const response = await fetch(`/api/projects/${projectId}`);
  const data = await handleResponse(response);
  // The project 'spec' field contains the file structure artifacts
  return data.spec || {};
};

export const fetchMessages = async (projectId) => {
  if (!projectId) return [];
  const response = await fetch(`/api/projects/${projectId}/messages`);
  const data = await handleResponse(response);
  return data.messages; // The endpoint returns { "messages": [...] }
};

export const fetchLogs = async (projectId) => {
  if (!projectId) return [];
  // No dedicated logs endpoint, re-using messages for now
  console.warn("API: fetchLogs is using fetchMessages as a fallback.");
  return fetchMessages(projectId);
};

export const connectToSSE = (projectId, onMessage) => {
  if (!projectId) {
    // Return a mock object that does nothing
    return { close: () => {} };
  }
  const eventSource = new EventSource(`/api/stream/${projectId}`);

  eventSource.onmessage = (event) => {
    onMessage(event);
  };

  eventSource.onerror = (err) => {
    console.error('EventSource failed:', err);
    eventSource.close();
  };

  return eventSource;
};

export const respondToAction = async (actionId, response) => {
  const res = await fetch('/api/actions/respond', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ action_id: actionId, response: response }),
  });
  return handleResponse(res);
};
