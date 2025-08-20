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

  const fetchResource = async (key, fetcher, setter) => {
    try {
      setLoading(prev => ({ ...prev, [key]: true }));
      setError(prev => ({ ...prev, [key]: null }));
      const data = await fetcher(); // No longer passing projectId
      
      // Defensive check to ensure data is valid
      if (data !== null && data !== undefined) {
        setter(data);
      } else {
        console.warn(`fetchResource: ${key} returned null/undefined data`);
        // Set appropriate default based on key
        if (key === 'agents') setter([]);
        else if (key === 'tasks') setter([]);
        else if (key === 'messages') setter([]);
        else if (key === 'logs') setter([]);
        else if (key === 'artifacts') setter({});
      }
    } catch (e) {
      console.error(`fetchResource error for ${key}:`, e);
      setError(prev => ({ ...prev, [key]: e.message }));
      
      // Set safe defaults on error
      if (key === 'agents') setter([]);
      else if (key === 'tasks') setter([]);
      else if (key === 'messages') setter([]);
      else if (key === 'logs') setter([]);
      else if (key === 'artifacts') setter({});
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
    console.log("AppContext useEffect triggered - Loading global data");
    
    // Fetch all resources using global endpoints
    fetchResource('agents', fetchAgents, setAgents);
    fetchResource('tasks', fetchTasks, setTasks);
    fetchResource('artifacts', fetchArtifacts, setArtifacts);
    fetchResource('messages', fetchMessages, setChatMessages);
    fetchResource('logs', fetchLogs, setLogs);

    // Connect to global SSE endpoint
    const sse = connectToSSE((event) => {
      try {
        const eventData = JSON.parse(event.data);
        console.log('SSE Event received:', eventData.type, eventData);
        
        switch (eventData.type) {
          case 'agent_update':
            if (eventData.payload) {
              setAgents(prevAgents => 
                prevAgents.map(agent => 
                  eventData.payload[agent.id] ? 
                    { ...agent, ...eventData.payload[agent.id] } : 
                    agent
                )
              );
            }
            break;
          case 'new_task':
            if (eventData.payload && Array.isArray(eventData.payload)) {
              setTasks(prevTasks => [...prevTasks, ...eventData.payload]);
            }
            break;
          case 'log_message':
            setLogs(prevLogs => [...prevLogs, eventData.payload]);
            break;
          case 'chat_message':
            setChatMessages((prevMessages) => [...prevMessages, eventData.payload]);
            break;
          case 'connected':
            console.log('SSE Connected successfully');
            break;
          default:
            console.warn('Unknown SSE event type:', eventData.type);
        }
      } catch (e) {
        console.error('Error parsing SSE event:', e);
      }
    });

    return () => {
      sse.close();
    };
  }, []); // Remove currentProject dependency

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
