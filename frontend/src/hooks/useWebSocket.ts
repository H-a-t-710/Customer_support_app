import { useState, useEffect, useRef, useCallback } from 'react';

type ConnectionStatus = 'Connecting' | 'Connected' | 'Disconnected' | 'Failed';

interface UseWebSocketReturn {
  sendMessage: (message: string) => void;
  lastMessage: string | null;
  connectionStatus: ConnectionStatus;
}

export function useWebSocket(url: string): UseWebSocketReturn {
  const [lastMessage, setLastMessage] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('Connecting');
  const socketRef = useRef<WebSocket | null>(null);
  
  // Set up WebSocket connection
  useEffect(() => {
    // Create WebSocket connection
    const socket = new WebSocket(url);
    socketRef.current = socket;
    
    // Connection opened
    socket.addEventListener('open', () => {
      setConnectionStatus('Connected');
      console.log('WebSocket connection established');
    });
    
    // Listen for messages
    socket.addEventListener('message', (event) => {
      setLastMessage(event.data);
    });
    
    // Connection closed
    socket.addEventListener('close', () => {
      setConnectionStatus('Disconnected');
      console.log('WebSocket connection closed');
    });
    
    // Connection error
    socket.addEventListener('error', (error) => {
      setConnectionStatus('Failed');
      console.error('WebSocket error:', error);
    });
    
    // Clean up on unmount
    return () => {
      if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
        socket.close();
      }
    };
  }, [url]);
  
  // Send message function
  const sendMessage = useCallback((message: string) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(message);
    } else {
      console.error('WebSocket is not connected');
    }
  }, []);
  
  return {
    sendMessage,
    lastMessage,
    connectionStatus,
  };
}

export default useWebSocket; 