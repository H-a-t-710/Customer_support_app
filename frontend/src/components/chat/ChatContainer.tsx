'use client';

import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { Message, MessageRole } from '@/types/chat';
import useWebSocket from '@/hooks/useWebSocket';
import { AlertCircle } from 'lucide-react';

export default function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => uuidv4());
  const [isClient, setIsClient] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Initialize WebSocket for real-time chat
  const { 
    lastMessage,
    sendMessage: sendWebSocketMessage,
    connectionStatus 
  } = useWebSocket(isClient ? `${process.env.NEXT_PUBLIC_API_WS_URL || 'ws://localhost:8000'}/api/chat/ws/${sessionId}` : '');
  
  // Process incoming WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage);
        
        if (data.type === 'status' && data.content === 'thinking') {
          setIsLoading(true);
        } else if (data.type === 'message') {
          setIsLoading(false);
          
          // Add assistant message
          setMessages(prev => [
            ...prev,
            {
              id: uuidv4(),
              content: data.content,
              role: MessageRole.ASSISTANT,
              createdAt: new Date().toISOString(),
              sources: data.sources
            }
          ]);
        } else if (data.type === 'error') {
          setIsLoading(false);
          console.error("WebSocket error:", data.content);
          
          // Show error message to user
          setMessages(prev => [
            ...prev,
            {
              id: uuidv4(),
              content: `Error: ${data.content}`,
              role: MessageRole.ASSISTANT,
              createdAt: new Date().toISOString()
            }
          ]);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    }
  }, [lastMessage]);
  
  // Send message via WebSocket
  const sendMessage = (message: string, includeWeb: boolean = true) => {
    // Don't send empty messages
    if (!message.trim()) return;
    
    // Add user message to the chat
    setMessages(prev => [
      ...prev,
      {
        id: uuidv4(),
        content: message,
        role: MessageRole.USER,
        createdAt: new Date().toISOString()
      }
    ]);
    
    // Set loading state
    setIsLoading(true);
    
    // Send message to WebSocket server
    sendWebSocketMessage(JSON.stringify({ 
      message: message.trim(),
      include_web: includeWeb 
    }));
  };
  
  // Fallback to REST API if WebSocket is not connected
  const sendMessageREST = async (message: string, includeWeb: boolean = true) => {
    try {
      setIsLoading(true);
      
      // Add user message
      setMessages(prev => [
        ...prev,
        {
          id: uuidv4(),
          content: message,
          role: MessageRole.USER,
          createdAt: new Date().toISOString()
        }
      ]);
      
      // Send message to API
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message.trim(),
          session_id: sessionId,
          include_web: includeWeb
        }),
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Add assistant response
      setMessages(prev => [
        ...prev,
        {
          id: uuidv4(),
          content: data.message,
          role: MessageRole.ASSISTANT,
          createdAt: new Date().toISOString(),
          sources: data.sources
        }
      ]);
      
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Show error message to user
      setMessages(prev => [
        ...prev,
        {
          id: uuidv4(),
          content: 'Sorry, there was an error processing your request. Please try again.',
          role: MessageRole.ASSISTANT,
          createdAt: new Date().toISOString()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle message submission based on connection status
  const handleSendMessage = (message: string, includeWeb: boolean = true) => {
    if (connectionStatus === 'Connected') {
      sendMessage(message, includeWeb);
    } else {
      sendMessageREST(message, includeWeb);
    }
  };
  
  // Check API connection on mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/health');
        if (response.ok) {
          setIsConnected(true);
        } else {
          setIsConnected(false);
          setError('Cannot connect to the backend server');
        }
      } catch (err) {
        setIsConnected(false);
        setError('Cannot connect to the backend server. Please ensure it is running.');
      }
    };
    
    checkConnection();
    
    // Set isClient to true when component mounts (client-side only)
    setIsClient(true);
    
    // Clean up error on unmount
    return () => {
      setError(null);
    };
  }, [setError]);

  // Handle errors
  useEffect(() => {
    if (error) {
      console.error('Chat error:', error);
    }
  }, [error]);

  // Show a simple loading state until client-side code takes over
  if (!isClient) {
    return <div className="chat-container flex flex-col p-4">Loading chat...</div>;
  }

  return (
    <div className="flex flex-col h-full bg-white rounded-none shadow-none">
      {!isConnected && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-none flex items-center justify-center text-sm font-medium mb-0 shadow-sm">
          <AlertCircle size={20} className="mr-2" />
          <span>Cannot connect to the backend server. Please ensure it is running.</span>
        </div>
      )}
      
      <MessageList messages={messages} isLoading={isLoading} />
      
      <div className="p-4 border-t border-angel-gray-200 bg-angel-gray-50 flex-shrink-0">
        <MessageInput onSendMessage={handleSendMessage} isLoading={isLoading} />
        
        {error && (
          <div className="mt-2 text-red-500 text-sm text-center">
            Error: {error}. Please try again.
          </div>
        )}
        
        {messages.length > 0 && (
          <div className="mt-4 text-center">
            <button 
              onClick={() => {
                setMessages([]);
                setError(null);
              }}
              className="text-sm text-violet-600 hover:text-violet-800 font-medium px-3 py-1 rounded-md bg-violet-50 hover:bg-violet-100 transition-colors duration-200"
            >
              Reset conversation
            </button>
          </div>
        )}
      </div>
    </div>
  );
} 