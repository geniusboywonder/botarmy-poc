import React, { createContext, useState, useEffect, useRef } from 'react';
import { fetchAgents, fetchTasks, fetchArtifacts, fetchMessages, fetchLogs, connectToSSE } from '../utils/api';

export const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [agents, setAgents] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [logs, setLogs] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [artifacts, setArtifacts] = useState({});
  const [loading, setLoading] = useState({ agents: true, tasks: true, artifacts: true, messages: true, logs: true });
  const [error, setError] = useState({ agents: null, tasks: null, artifacts: null, messages: null, logs: null });
  const chatEndRef = useRef(null);
  const logsEndRef = useRef(null);

  const fetchResource = async (key, fetcher, setter) => {
    try {
      setLoading(prev => ({ ...prev, [key]: true }));
      setError(prev => ({ ...prev, [key]: null }));
      const data = await fetcher();
      setter(data);
    } catch (e) {
      setError(prev => ({ ...prev, [key]: e.message }));
    } finally {
      setLoading(prev => ({ ...prev, [key]: false }));
    }
  };

  const refetch = (key) => {
    const resourceMap = {
      agents: () => fetchResource('agents', fetchAgents, setAgents),
      tasks: () => fetchResource('tasks', fetchTasks, setTasks),
      artifacts: () => fetchResource('artifacts', fetchArtifacts, setArtifacts),
      messages: () => fetchResource('messages', fetchMessages, setChatMessages),
      logs: () => fetchResource('logs', fetchLogs, setLogs),
    };
    if (resourceMap[key]) {
      resourceMap[key]();
    }
  };

  useEffect(() => {
    fetchResource('agents', fetchAgents, setAgents);
    fetchResource('tasks', fetchTasks, setTasks);
    fetchResource('artifacts', fetchArtifacts, setArtifacts);
    fetchResource('messages', fetchMessages, setChatMessages);
    fetchResource('logs', fetchLogs, setLogs);

    const sse = connectToSSE((event) => {
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
  }, []);

  const value = {
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
