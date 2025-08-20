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

export const fetchAgents = async () => {
  // Use new global agents endpoint
  const response = await fetch('/api/agents');
  const data = await handleResponse(response);
  return data.agents; // The endpoint returns { "agents": [...] }
};

export const fetchTasks = async () => {
  // Use new global tasks endpoint
  const response = await fetch('/api/tasks');
  const data = await handleResponse(response);
  return data.tasks; // The endpoint returns { "tasks": [...] }
};

export const fetchArtifacts = async () => {
  // Use new global artifacts endpoint
  const response = await fetch('/api/artifacts');
  const data = await handleResponse(response);
  
  // Ensure we always return a valid artifacts structure
  const artifacts = data.artifacts || {};
  
  // Ensure each category is an array (defensive programming)
  const categories = ['requirements', 'design', 'testing', 'deployment', 'maintenance'];
  categories.forEach(category => {
    if (!Array.isArray(artifacts[category])) {
      artifacts[category] = [];
    }
  });
  
  // Handle development category specially (it has subcategories)
  if (!artifacts.development || typeof artifacts.development !== 'object') {
    artifacts.development = { source_code: [], documentation: [] };
  }
  if (!Array.isArray(artifacts.development.source_code)) {
    artifacts.development.source_code = [];
  }
  if (!Array.isArray(artifacts.development.documentation)) {
    artifacts.development.documentation = [];
  }
  
  return artifacts;
};

export const fetchMessages = async () => {
  // Use new global messages endpoint
  const response = await fetch('/api/messages');
  const data = await handleResponse(response);
  return data.messages; // The endpoint returns { "messages": [...] }
};

export const fetchLogs = async () => {
  // Use new global logs endpoint
  const response = await fetch('/api/logs');
  const data = await handleResponse(response);
  return data.logs; // The endpoint returns { "logs": [...] }
};

export const connectToSSE = (onMessage) => {
  // Use new global events endpoint
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
