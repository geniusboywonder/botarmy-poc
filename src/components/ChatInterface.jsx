import React, { useState, useRef, useEffect } from 'react';
import { Send, Pause, Play, AlertCircle } from 'lucide-react';

/**
 * Chat Interface Component with @Agent Mention Support
 * 
 * Features:
 * - @agent mention parsing and highlighting
 * - Human-in-loop permission requests
 * - Real-time chat history
 * - Agent status monitoring
 * - Manual workflow control
 */

const ChatInterface = ({ 
  agents = [], 
  chatHistory = [], 
  onSendMessage, 
  onPauseAgent, 
  onResumeAgent,
  className = "" 
}) => {
  const [inputValue, setInputValue] = useState('');
  const [mentionedAgents, setMentionedAgents] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const inputRef = useRef(null);
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  // Parse @agent mentions in input text
  const parseMentions = (text) => {
    const mentionRegex = /@(\w+)/g;
    const mentions = [];
    let match;
    
    while ((match = mentionRegex.exec(text)) !== null) {
      const agentName = match[1].toLowerCase();
      const agent = agents.find(a => a.id.toLowerCase() === agentName);
      if (agent) {
        mentions.push(agent);
      }
    }
    
    return mentions;
  };

  // Handle input change and mention detection
  const handleInputChange = (e) => {
    const value = e.target.value;
    setInputValue(value);
    
    const mentions = parseMentions(value);
    setMentionedAgents(mentions);
  };

  // Handle message submission
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!inputValue.trim()) return;

    const mentions = parseMentions(inputValue);
    
    if (mentions.length === 0) {
      // No mentions - general system message
      onSendMessage({
        type: 'system',
        content: inputValue.trim(),
        timestamp: new Date().toISOString(),
        mentioned_agents: []
      });
    } else {
      // Send to first mentioned agent (primary target)
      const primaryAgent = mentions[0];
      onSendMessage({
        message_type: 'user_command',
        content: inputValue.trim(),
        target_agent: primaryAgent.id,
        timestamp: new Date().toISOString(),
        mentioned_agents: mentions.map(a => a.id)
      });
    }

    setInputValue('');
    setMentionedAgents([]);
  };

  // Render message with @mention highlighting
  const renderMessageContent = (content) => {
    const mentionRegex = /@(\w+)/g;
    const parts = content.split(mentionRegex);
    
    return parts.map((part, index) => {
      if (index % 2 === 1) {
        // This is a mentioned agent name
        const agent = agents.find(a => a.id.toLowerCase() === part.toLowerCase());
        if (agent) {
          return (
            <span 
              key={index} 
              className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-1 rounded font-medium"
            >
              @{part}
            </span>
          );
        }
      }
      return part;
    });
  };

  // Get agent status color
  const getAgentStatusColor = (status) => {
    switch (status) {
      case 'working': return 'text-yellow-500';
      case 'idle': return 'text-green-500';
      case 'paused': return 'text-red-500';
      case 'error': return 'text-red-600';
      default: return 'text-gray-500';
    }
  };

  // Get message type styling
  const getMessageTypeStyles = (message) => {
    switch (message.type) {
      case 'user_command':
        return 'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-l-blue-500';
      case 'agent_response':
        return 'bg-green-50 dark:bg-green-900/20 border-l-4 border-l-green-500';
      case 'agent_request':
        return 'bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-l-yellow-500';
      case 'system':
        return 'bg-gray-50 dark:bg-gray-800 border-l-4 border-l-gray-400';
      case 'error':
        return 'bg-red-50 dark:bg-red-900/20 border-l-4 border-l-red-500';
      default:
        return 'bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600';
    }
  };

  return (
    <div className={`flex flex-col h-full bg-white dark:bg-gray-800 rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-600">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Human-in-Loop Chat
          </h3>
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
            <AlertCircle className="w-4 h-4" />
            <span>Use @agent mentions to direct commands</span>
          </div>
        </div>
        
        {/* Agent Status Strip */}
        <div className="mt-3 flex flex-wrap gap-2">
          {agents.map(agent => (
            <div key={agent.id} className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${getAgentStatusColor(agent.status)}`} />
              <span className="text-sm text-gray-600 dark:text-gray-300">
                {agent.id}
              </span>
              
              {/* Pause/Resume Button */}
              <button
                onClick={() => agent.status === 'paused' ? onResumeAgent(agent.id) : onPauseAgent(agent.id)}
                className="ml-1 p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                title={agent.status === 'paused' ? 'Resume Agent' : 'Pause Agent'}
              >
                {agent.status === 'paused' ? (
                  <Play className="w-3 h-3" />
                ) : (
                  <Pause className="w-3 h-3" />
                )}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {chatHistory.length === 0 ? (
          <div className="text-center text-gray-500 dark:text-gray-400 mt-8">
            <div className="mb-2">💬</div>
            <p className="text-sm">No messages yet. Try:</p>
            <div className="mt-2 text-xs space-y-1">
              <p><code>@analyst analyze the current requirements</code></p>
              <p><code>@developer what are you working on?</code></p>
              <p><code>@architect show me the system design</code></p>
            </div>
          </div>
        ) : (
          chatHistory.map((message, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg ${getMessageTypeStyles(message)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* Message Header */}
                  <div className="flex items-center gap-2 mb-1">
                    {message.type === 'user_command' && (
                      <span className="text-xs font-medium text-blue-600 dark:text-blue-400">
                        YOU
                      </span>
                    )}
                    {message.type === 'agent_response' && (
                      <span className="text-xs font-medium text-green-600 dark:text-green-400">
                        {message.fromAgent?.toUpperCase() || 'AGENT'}
                      </span>
                    )}
                    {message.type === 'agent_request' && (
                      <span className="text-xs font-medium text-yellow-600 dark:text-yellow-400">
                        {message.fromAgent?.toUpperCase() || 'AGENT'} REQUESTS PERMISSION
                      </span>
                    )}
                    {message.type === 'system' && (
                      <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                        SYSTEM
                      </span>
                    )}
                    
                    <span className="text-xs text-gray-400 dark:text-gray-500">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  
                  {/* Message Content */}
                  <div className="text-sm text-gray-800 dark:text-gray-200">
                    {renderMessageContent(message.content)}
                  </div>
                  
                  {/* Permission Request Actions */}
                  {message.type === 'agent_request' && message.awaitingPermission && (
                    <div className="mt-3 flex gap-2">
                      <button
                        onClick={() => message.onApprove?.(message.requestId)}
                        className="px-3 py-1 bg-green-500 hover:bg-green-600 text-white text-xs rounded"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => message.onReject?.(message.requestId)}
                        className="px-3 py-1 bg-red-500 hover:bg-red-600 text-white text-xs rounded"
                      >
                        Reject
                      </button>
                      <button
                        onClick={() => message.onModify?.(message.requestId)}
                        className="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded"
                      >
                        Modify
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-600">
        {/* Mention Preview */}
        {mentionedAgents.length > 0 && (
          <div className="mb-2 text-xs text-gray-600 dark:text-gray-400">
            Mentioning: {mentionedAgents.map(agent => (
              <span key={agent.id} className="ml-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-1 rounded">
                @{agent.id}
              </span>
            ))}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            placeholder="Type a message... Use @agent to mention agents"
            className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md 
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                     focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isTyping}
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isTyping}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 
                     text-white rounded-md transition-colors duration-200
                     flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            Send
          </button>
        </form>
        
        {/* Typing Indicator */}
        {isTyping && (
          <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
            <div className="animate-pulse">Agent is typing...</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
