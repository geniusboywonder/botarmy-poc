import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";

// Global state context
const AppContext = createContext();

// Main App component
export default function App() {
  const [state, setState] = useState({
    project: null,
    messages: [],
    actions: [],
    agents: {
      analyst: { status: "idle", current_task: null },
      architect: { status: "idle", current_task: null },
      developer: { status: "idle", current_task: null },
      tester: { status: "idle", current_task: null },
    },
    connected: false,
  });

  const updateState = (updates) => {
    setState((prev) => ({ ...prev, ...updates }));
  };

  return (
    <AppContext.Provider value={{ ...state, updateState }}>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          {!state.project ? <ProjectSetup /> : <Dashboard />}
        </main>
      </div>
    </AppContext.Provider>
  );
}

// Header component
function Header() {
  const { project } = useContext(AppContext);

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">BotArmy POC</h1>
          {project && (
            <div className="text-sm text-gray-600">
              Project: <span className="font-medium">{project.name}</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

// Project setup form
function ProjectSetup() {
  const { updateState } = useContext(AppContext);
  const [formData, setFormData] = useState({
    name: "",
    requirements: "",
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch("/api/projects", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();

        // Fetch project details
        const projectResponse = await fetch(`/api/projects/${data.project_id}`);
        const project = await projectResponse.json();

        updateState({ project });

        // Start SSE connection
        startSSEConnection(data.project_id, updateState);
      } else {
        console.error("Failed to create project");
      }
    } catch (error) {
      console.error("Error creating project:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Create New Project</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Project Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, name: e.target.value }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter project name..."
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Requirements
            </label>
            <textarea
              value={formData.requirements}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  requirements: e.target.value,
                }))
              }
              rows={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe what you want to build..."
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Creating Project..." : "Create Project"}
          </button>
        </form>
      </div>
    </div>
  );
}

// Main dashboard
function Dashboard() {
  const { project, messages, actions, agents, connected } =
    useContext(AppContext);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Agent Status Panel */}
      <div className="lg:col-span-1">
        <AgentStatusPanel agents={agents} connected={connected} />
      </div>

      {/* Main Content */}
      <div className="lg:col-span-2">
        <MessagePanel messages={messages} />
      </div>

      {/* Action Queue */}
      <div className="lg:col-span-1">
        <ActionPanel actions={actions} />
      </div>
    </div>
  );
}

// Agent status panel
function AgentStatusPanel({ agents, connected }) {
  const getStatusColor = (status) => {
    switch (status) {
      case "thinking":
        return "bg-yellow-100 text-yellow-800";
      case "waiting":
        return "bg-blue-100 text-blue-800";
      case "error":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "thinking":
        return "🤔";
      case "waiting":
        return "⏳";
      case "error":
        return "❌";
      default:
        return "⚪";
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Agent Status</h3>
        <div
          className={`px-2 py-1 rounded-full text-xs ${connected ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
        >
          {connected ? "Connected" : "Disconnected"}
        </div>
      </div>

      <div className="space-y-3">
        {Object.entries(agents).map(([agentId, agent]) => (
          <div key={agentId} className="border rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium capitalize">{agentId}</span>
              <span className="text-lg">{getStatusIcon(agent.status)}</span>
            </div>

            <div
              className={`px-2 py-1 rounded-full text-xs ${getStatusColor(agent.status)}`}
            >
              {agent.status}
            </div>

            {agent.current_task && (
              <div className="mt-2 text-xs text-gray-600">
                {agent.current_task}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// Message panel
function MessagePanel({ messages }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold mb-4">Agent Conversations</h3>

      <div className="space-y-4 max-h-96 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            No messages yet. Agents will start working once the project is
            created.
          </div>
        ) : (
          messages.map((message, index) => (
            <MessageBubble key={index} message={message} />
          ))
        )}
      </div>
    </div>
  );
}

// Individual message bubble
function MessageBubble({ message }) {
  const getAgentColor = (agent) => {
    const colors = {
      analyst: "bg-blue-100 text-blue-800",
      architect: "bg-green-100 text-green-800",
      developer: "bg-purple-100 text-purple-800",
      tester: "bg-orange-100 text-orange-800",
      system: "bg-gray-100 text-gray-800",
    };
    return colors[agent] || "bg-gray-100 text-gray-800";
  };

  return (
    <div className="border rounded-lg p-3">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span
            className={`px-2 py-1 rounded-full text-xs ${getAgentColor(message.from_agent)}`}
          >
            {message.from_agent}
          </span>
          {message.to_agent && (
            <>
              <span className="text-gray-400">→</span>
              <span
                className={`px-2 py-1 rounded-full text-xs ${getAgentColor(message.to_agent)}`}
              >
                {message.to_agent}
              </span>
            </>
          )}
        </div>

        <div className="flex items-center space-x-2">
          {message.confidence && (
            <span className="text-xs text-gray-500">
              {Math.round(message.confidence * 100)}%
            </span>
          )}
          <span className="text-xs text-gray-500">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        </div>
      </div>

      <div className="text-sm">
        {typeof message.content === "string" ? (
          <p>{message.content}</p>
        ) : (
          <details className="cursor-pointer">
            <summary className="font-medium">
              {message.message_type}:{" "}
              {message.content.summary || "View Details"}
            </summary>
            <pre className="mt-2 text-xs bg-gray-50 p-2 rounded overflow-x-auto">
              {JSON.stringify(message.content, null, 2)}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
}

// Action panel for human interventions
function ActionPanel({ actions }) {
  const { updateState } = useContext(AppContext);

  const handleActionResponse = async (actionId, response) => {
    try {
      await fetch("/api/actions/respond", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          action_id: actionId,
          response: response,
        }),
      });

      // Remove action from list
      updateState({
        actions: actions.filter((action) => action.id !== actionId),
      });
    } catch (error) {
      console.error("Error responding to action:", error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold mb-4">Action Required</h3>

      {actions.length === 0 ? (
        <div className="text-center text-gray-500 py-8">
          No actions required
        </div>
      ) : (
        <div className="space-y-4">
          {actions.map((action) => (
            <ActionItem
              key={action.id}
              action={action}
              onRespond={handleActionResponse}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Individual action item
function ActionItem({ action, onRespond }) {
  const [selectedOption, setSelectedOption] = useState("");
  const [customResponse, setCustomResponse] = useState("");

  const handleSubmit = () => {
    const response = selectedOption || customResponse;
    if (response.trim()) {
      onRespond(action.id, response);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "urgent":
        return "bg-red-100 text-red-800 border-red-200";
      case "high":
        return "bg-orange-100 text-orange-800 border-orange-200";
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      default:
        return "bg-blue-100 text-blue-800 border-blue-200";
    }
  };

  return (
    <div
      className={`border rounded-lg p-4 ${getPriorityColor(action.priority)}`}
    >
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-medium">{action.title}</h4>
        <span className="text-xs px-2 py-1 rounded-full bg-white bg-opacity-50">
          {action.priority}
        </span>
      </div>

      <p className="text-sm mb-3">{action.description}</p>

      {action.options && action.options.length > 0 && (
        <div className="mb-3">
          <label className="block text-xs font-medium mb-2">
            Choose an option:
          </label>
          <select
            value={selectedOption}
            onChange={(e) => setSelectedOption(e.target.value)}
            className="w-full px-2 py-1 text-sm border rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">Select option...</option>
            {action.options.map((option, index) => (
              <option key={index} value={option.id || option}>
                {option.label || option}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="mb-3">
        <label className="block text-xs font-medium mb-2">
          Or provide custom response:
        </label>
        <textarea
          value={customResponse}
          onChange={(e) => setCustomResponse(e.target.value)}
          rows={3}
          className="w-full px-2 py-1 text-sm border rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="Enter your response..."
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={!selectedOption && !customResponse.trim()}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Submit Response
      </button>
    </div>
  );
}

// Server-Sent Events connection
function startSSEConnection(projectId, updateState) {
  const eventSource = new EventSource(`/api/stream/${projectId}`);

  eventSource.onopen = () => {
    updateState({ connected: true });
  };

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case "connected":
          updateState({ connected: true });
          break;

        case "message":
          updateState((prevState) => ({
            messages: [...prevState.messages, data].slice(-50), // Keep last 50 messages
          }));
          break;

        case "action":
          updateState((prevState) => ({
            actions: [...prevState.actions, data],
          }));
          break;

        case "agent_status":
          updateState({ agents: data.agents });
          break;

        case "error":
          console.error("SSE error:", data.message);
          break;
      }
    } catch (error) {
      console.error("Error parsing SSE data:", error);
    }
  };

  eventSource.onerror = () => {
    updateState({ connected: false });

    // Attempt to reconnect after 5 seconds
    setTimeout(() => {
      startSSEConnection(projectId, updateState);
    }, 5000);
  };

  return eventSource;
}
