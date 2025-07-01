import { useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Message, MessageRole } from '@/types/chat';
import { sendMessage } from '@/services/chatService';
import useChatStore from '@/store/chatStore';

interface UseChatProps {
  initialMessages?: Message[];
}

export function useChat({ initialMessages = [] }: UseChatProps = {}) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  const storeState = useChatStore();

  const addMessage = useCallback((content: string, role: MessageRole) => {
    const newMessage: Message = {
      id: uuidv4(),
      content,
      role,
      createdAt: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, newMessage]);
    return newMessage;
  }, []);

  const sendUserMessage = useCallback(async (content: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Add user message to local state
      addMessage(content, MessageRole.USER);
      
      // Send message to API
      const response = await sendMessage({ content });
      
      // Add assistant response to local state
      if (response.message) {
        addMessage(response.message.content, MessageRole.ASSISTANT);
      }
      
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      console.error('Error sending message:', err);
    } finally {
      setIsLoading(false);
    }
  }, [addMessage]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage: sendUserMessage,
    addMessage,
    clearMessages,
  };
} 