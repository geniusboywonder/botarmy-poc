import React, { createContext, useState, useEffect, useRef } from 'react';
import { fetchAgents, fetchTasks, fetchArtifacts, fetchMessages, fetchLogs, connectToSSE } from '../utils/api';

export const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [agents, setAgents] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [logs, setLogs] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [artifacts, setArtifacts] = useState({});
  const chatEndRef = useRef(null);
  const logsEndRef = useRef(null);

  useEffect(() => {
    fetchAgents().then(setAgents);
    fetchTasks().then(setTasks);
    fetchArtifacts().then(setArtifacts);
    fetchMessages().then(setChatMessages);
    fetchLogs().then(setLogs);

    const sse = connectToSSE((event) => {
      const newMessage = JSON.parse(event.data);
      setChatMessages((prevMessages) => [...prevMessages, newMessage]);
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
    chatEndRef,
    logsEndRef,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
