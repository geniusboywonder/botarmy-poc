import React, { createContext, useState, useEffect, useRef } from 'react';
import { fetchAgents, fetchTasks, fetchArtifacts, fetchMessages, fetchLogs, connectToSSE } from '../utils/api';

export const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [currentProject, setCurrentProject] = useState('proj_49583');
  const [agents, setAgents] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [logs, setLogs] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [artifacts, setArtifacts] = useState({});
  const [loading, setLoading] = useState({ agents: true, tasks: true, artifacts: true, messages: true, logs: true });
  const [error, setError] = useState({ agents: null, tasks: null, artifacts: null, messages: null, logs: null });
  const chatEndRef = useRef(null);
  const logsEndRef = useRef(null);

  const fetchResource = async (key, fetcher, setter, projectId) => {
    try {
      setLoading(prev => ({ ...prev, [key]: true }));
      setError(prev => ({ ...prev, [key]: null }));
      const data = await fetcher(projectId);
      setter(data);
    } catch (e) {
      setError(prev => ({ ...prev, [key]: e.message }));
    } finally {
      setLoading(prev => ({ ...prev, [key]: false }));
    }
  };

  const refetch = (key) => {
    const resourceMap = {
      agents: () => fetchResource('agents', fetchAgents, setAgents, currentProject),
      tasks: () => fetchResource('tasks', fetchTasks, setTasks, currentProject),
      artifacts: () => fetchResource('artifacts', fetchArtifacts, setArtifacts, currentProject),
      messages: () => fetchResource('messages', fetchMessages, setChatMessages, currentProject),
      logs: () => fetchResource('logs', fetchLogs, setLogs, currentProject),
    };
    if (resourceMap[key]) {
      resourceMap[key]();
    }
  };

  useEffect(() => {
    console.log("AppContext useEffect triggered. Project ID:", currentProject);
    if (currentProject) {
      fetchResource('agents', fetchAgents, setAgents, currentProject);
      fetchResource('tasks', fetchTasks, setTasks, currentProject);
      fetchResource('artifacts', fetchArtifacts, setArtifacts, currentProject);
      fetchResource('messages', fetchMessages, setChatMessages, currentProject);
      fetchResource('logs', fetchLogs, setLogs, currentProject);

      const sse = connectToSSE(currentProject, (event) => {
        const eventData = JSON.parse(event.data);
        switch (eventData.type) {
          case 'agent_update':
            setAgents(prevAgents => prevAgents.map(agent => agent.id === eventData.payload.id ? { ...agent, ...eventData.payload } : agent));
            break;
          case 'new_task':
            setTasks(prevTasks => [...prevTasks, eventData.payload]);
            break;
          case 'log_message':
            setLogs(prevLogs => [...prevLogs, eventData.payload]);
            break;
          case 'chat_message':
            setChatMessages((prevMessages) => [...prevMessages, eventData.payload]);
            break;
          default:
            console.warn('Unknown SSE event type:', eventData.type);
        }
      });

      return () => {
        sse.close();
      };
    }
  }, [currentProject]);

  const value = {
    currentProject,
    setCurrentProject,
    agents,
    setAgents,
    chatMessages,
    setChatMessages,
    logs,
    setLogs,
    tasks,
    setTasks,
    artifacts,
    setArtifacts,
    loading,
    error,
    refetch,
    chatEndRef,
    logsEndRef,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
