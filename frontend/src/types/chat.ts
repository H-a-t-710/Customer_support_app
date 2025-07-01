/**
 * Types related to chat functionality
 */

export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system',
}

export interface Source {
  content: string;
  metadata: {
    source: string;
    page?: number | string;
    chunk?: number;
    source_type?: string;
  };
  similarity: number;
}

export interface Message {
  id: string;
  content: string;
  role: MessageRole;
  createdAt: string;
  sources?: Source[];
}

export interface ChatSession {
  id: string;
  name: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

export interface ChatState {
  sessions: Record<string, ChatSession>;
  currentSessionId: string | null;
  isLoading: boolean;
  error: string | null;
}

export interface CreateMessageRequest {
  message: string;
  session_id?: string;
  include_web?: boolean;
}

export interface CreateMessageResponse {
  message: string;
  sources?: Source[];
  session_id: string;
}

export interface ChatHistoryResponse {
  sessions: ChatSession[];
}

export interface SessionResponse {
  session_id: string;
  messages: Message[];
}

export enum ChatEventType {
  MESSAGE_RECEIVED = 'message_received',
  THINKING = 'thinking',
  ERROR = 'error',
}

export interface ChatEvent {
  type: ChatEventType;
  data: any;
} 