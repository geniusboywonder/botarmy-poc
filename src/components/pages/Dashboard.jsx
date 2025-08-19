import React, { useState, useEffect, useContext } from 'react';
import AgentPanel from '../AgentPanel';
import ActionQueue from '../ActionQueue';
import ProjectViewer from '../ProjectViewer';
import RealtimeLog from '../shared/RealtimeLog';
import ChatInterface from '../ChatInterface';
import { AppContext } from '../../context/AppContext';

const Dashboard = () => {
  const { agents } = useContext(AppContext);
  const [chatHistory, setChatHistory] = useState([]);
  const [showChat, setShowChat] = useState(true);

  // Load chat history on component mount
  useEffect(() => {
    fetchChatHistory();
  }, []);

  const fetchChatHistory = async () => {
    try {
      const response = await fetch('/api/chat/history');
      const data = await response.json();
      setChatHistory(data.messages || []);
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
    }
  };

  const handleSendMessage = async (message) => {
    try {
      const response = await fetch('/api/chat/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(message),
      });

      if (response.ok) {
        // Refresh chat history
        fetchChatHistory();
      } else {
        console.error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handlePauseAgent = async (agentId) => {
    try {
      const response = await fetch('/api/agents/action', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_id: agentId,
          action: 'pause'
        }),
      });

      if (response.ok) {
        fetchChatHistory();
      } else {
        console.error('Failed to pause agent');
      }
    } catch (error) {
      console.error('Error pausing agent:', error);
    }
  };

  const handleResumeAgent = async (agentId) => {
    try {
      const response = await fetch('/api/agents/action', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_id: agentId,
          action: 'resume'
        }),
      });

      if (response.ok) {
        fetchChatHistory();
      } else {
        console.error('Failed to resume agent');
      }
    } catch (error) {
      console.error('Error resuming agent:', error);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
      {/* Left Column: Agents and Actions */}
      <div className="lg:col-span-1 flex flex-col gap-6">
        <AgentPanel />
        <ActionQueue />
      </div>
      
      {/* Right Column: Chat Interface */}
      <div className="lg:col-span-2">
        {showChat ? (
          <ChatInterface
            agents={agents}
            chatHistory={chatHistory}
            onSendMessage={handleSendMessage}
            onPauseAgent={handlePauseAgent}
            onResumeAgent={handleResumeAgent}
            className="h-full"
          />
        ) : (
          <RealtimeLog />
        )}
        
        {/* Toggle between Chat and Logs */}
        <div className="mt-4 flex justify-center">
          <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-1 flex">
            <button
              onClick={() => setShowChat(true)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                showChat 
                  ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm' 
                  : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Chat
            </button>
            <button
              onClick={() => setShowChat(false)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                !showChat 
                  ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm' 
                  : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              System Logs
            </button>
          </div>
        </div>
      </div>
      
      {/* Bottom Row: Project Viewer */}
      <div className="lg:col-span-3">
        <ProjectViewer />
      </div>
    </div>
  );
};

export default Dashboard;
