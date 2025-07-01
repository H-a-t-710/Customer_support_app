import { 
  CreateMessageRequest, 
  CreateMessageResponse,
  ChatHistoryResponse,
  SessionResponse,
  Message,
  MessageRole
} from '@/types/chat';
import { v4 as uuidv4 } from 'uuid';
import { API_URL } from '@/lib/constants';

/**
 * Send a message to the chatbot API
 */
export async function sendMessage(data: { content: string, sessionId?: string }): Promise<CreateMessageResponse> {
  try {
    // Convert from frontend format to backend format
    const requestData: CreateMessageRequest = {
      message: data.content,
      session_id: data.sessionId
    };

    // The backend route is defined as /message under the /api/chat prefix
    const response = await fetch(`${API_URL}/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Error ${response.status}: ${response.statusText}`);
    }

    const responseData = await response.json();
    
    // Convert from backend format to frontend format
    return {
      message: responseData.message,
      sources: responseData.sources,
      session_id: responseData.session_id
    };
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
}

/**
 * Fetch chat sessions
 */
export async function fetchSessions(): Promise<ChatHistoryResponse> {
  try {
    const response = await fetch(`${API_URL}/chat/sessions`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Error ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching sessions:', error);
    throw error;
  }
}

/**
 * Fetch a specific chat session
 */
export async function fetchSession(sessionId: string): Promise<SessionResponse> {
  try {
    const response = await fetch(`${API_URL}/chat/history/${sessionId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Error ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Error fetching session ${sessionId}:`, error);
    throw error;
  }
}

/**
 * Delete a chat session
 */
export async function deleteSession(sessionId: string): Promise<void> {
  try {
    const response = await fetch(`${API_URL}/chat/sessions/${sessionId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Error ${response.status}: ${response.statusText}`);
    }
  } catch (error) {
    console.error(`Error deleting session ${sessionId}:`, error);
    throw error;
  }
} 