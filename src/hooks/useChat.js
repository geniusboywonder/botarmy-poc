import { useState, useRef } from 'react';

export function useChat() {
  const [chatMessages, setChatMessages] = useState([]);
  const [logs, setLogs] = useState([]);
  const chatEndRef = useRef(null);
  const logsEndRef = useRef(null);

  return {
    chatMessages,
    setChatMessages,
    logs,
    setLogs,
    chatEndRef,
    logsEndRef,
  };
}
