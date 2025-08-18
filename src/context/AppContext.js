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

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(prev => ({ ...prev, agents: true }));
        const agentsData = await fetchAgents();
        setAgents(agentsData);
      } catch (e) {
        setError(prev => ({ ...prev, agents: e.message }));
      } finally {
        setLoading(prev => ({ ...prev, agents: false }));
      }

      try {
        setLoading(prev => ({ ...prev, tasks: true }));
        const tasksData = await fetchTasks();
        setTasks(tasksData);
      } catch (e) {
        setError(prev => ({ ...prev, tasks: e.message }));
      } finally {
        setLoading(prev => ({ ...prev, tasks: false }));
      }

      try {
        setLoading(prev => ({ ...prev, artifacts: true }));
        const artifactsData = await fetchArtifacts();
        setArtifacts(artifactsData);
      } catch (e) {
        setError(prev => ({ ...prev, artifacts: e.message }));
      } finally {
        setLoading(prev => ({ ...prev, artifacts: false }));
      }

        try {
            setLoading(prev => ({ ...prev, messages: true }));
            const messagesData = await fetchMessages();
            setChatMessages(messagesData);
        } catch (e) {
            setError(prev => ({ ...prev, messages: e.message }));
        } finally {
            setLoading(prev => ({ ...prev, messages: false }));
        }

        try {
            setLoading(prev => ({ ...prev, logs: true }));
            const logsData = await fetchLogs();
            setLogs(logsData);
        } catch (e) {
            setError(prev => ({ ...prev, logs: e.message }));
        } finally {
            setLoading(prev => ({ ...prev, logs: false }));
        }
    };

    fetchData();

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
    chatEndRef,
    logsEndRef,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
