import { create } from 'zustand';
import { v4 as uuidv4 } from 'uuid';
import { persist, createJSONStorage } from 'zustand/middleware';
import { 
  ChatState,
  Message, 
  MessageRole, 
  ChatSession,
  Source
} from '@/types/chat';
import { sendMessage, fetchSession } from '@/services/chatService';

// Check if code is running on client side
const isClient = typeof window !== 'undefined';

interface ChatStore extends ChatState {
  // Session actions
  createSession: () => string;
  switchSession: (sessionId: string) => void;
  renameSession: (sessionId: string, name: string) => void;
  deleteSession: (sessionId: string) => void;
  clearSessions: () => void;
  
  // Message actions
  sendMessage: (content: string) => Promise<void>;
  addMessage: (message: Message, sessionId?: string) => void;
  updateMessage: (messageId: string, content: string, sessionId?: string) => void;
  deleteMessage: (messageId: string, sessionId?: string) => void;
  clearMessages: (sessionId?: string) => void;
  
  // State management
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  
  // Session retrieval
  getCurrentSession: () => ChatSession | null;
  getMessages: () => Message[];
}

const createDefaultSession = (): ChatSession => ({
  id: uuidv4(),
  name: 'New Chat',
  messages: [],
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
});

const useChatStore = create<ChatStore>()(
  persist(
    (set, get) => ({
      sessions: {},
      currentSessionId: null,
      isLoading: false,
      error: null,
      
      // Session actions
      createSession: () => {
        const newSession = createDefaultSession();
        set(state => ({
          sessions: {
            ...state.sessions,
            [newSession.id]: newSession
          },
          currentSessionId: newSession.id
        }));
        return newSession.id;
      },
      
      switchSession: (sessionId: string) => {
        if (get().sessions[sessionId]) {
          set({ currentSessionId: sessionId });
        }
      },
      
      renameSession: (sessionId: string, name: string) => {
        set(state => {
          if (!state.sessions[sessionId]) return state;
          
          const updatedSession = {
            ...state.sessions[sessionId],
            name,
            updatedAt: new Date().toISOString()
          };
          
          return {
            sessions: {
              ...state.sessions,
              [sessionId]: updatedSession
            }
          };
        });
      },
      
      deleteSession: (sessionId: string) => {
        set(state => {
          const { [sessionId]: _, ...restSessions } = state.sessions;
          
          // If we're deleting the current session, switch to another
          let currentSessionId = state.currentSessionId;
          if (currentSessionId === sessionId) {
            const sessionIds = Object.keys(restSessions);
            currentSessionId = sessionIds.length > 0 ? sessionIds[0] : null;
          }
          
          return {
            sessions: restSessions,
            currentSessionId
          };
        });
      },
      
      clearSessions: () => {
        set({ 
          sessions: {},
          currentSessionId: null 
        });
      },
      
      // Message actions
      sendMessage: async (content: string) => {
        try {
          set({ isLoading: true, error: null });
          
          let { currentSessionId } = get();
          
          // Create session if none exists
          if (!currentSessionId || !get().sessions[currentSessionId]) {
            currentSessionId = get().createSession();
          }
          
          // Add user message
          const userMessage: Message = {
            id: uuidv4(),
            content,
            role: MessageRole.USER,
            createdAt: new Date().toISOString()
          };
          
          get().addMessage(userMessage, currentSessionId);
          
          // Send to API
          const response = await sendMessage({
            content,
            sessionId: currentSessionId
          });
          
          // Add assistant response
          const assistantMessage: Message = {
            id: uuidv4(),
            content: response.message,
            role: MessageRole.ASSISTANT,
            createdAt: new Date().toISOString(),
            sources: response.sources
          };
          
          get().addMessage(assistantMessage, currentSessionId);
          
        } catch (error) {
          console.error('Error sending message:', error);
          set({ error: error instanceof Error ? error.message : 'Failed to send message' });
        } finally {
          set({ isLoading: false });
        }
      },
      
      addMessage: (message: Message, sessionId?: string) => {
        const targetSessionId = sessionId || get().currentSessionId;
        
        if (!targetSessionId) {
          console.error('No session ID provided or selected');
          return;
        }
        
        set(state => {
          // Create session if it doesn't exist
          const session = state.sessions[targetSessionId] || createDefaultSession();
          
          const updatedSession = {
            ...session,
            id: targetSessionId,
            messages: [...session.messages, message],
            updatedAt: new Date().toISOString()
          };
          
          return {
            sessions: {
              ...state.sessions,
              [targetSessionId]: updatedSession
            },
            currentSessionId: targetSessionId
          };
        });
      },
      
      updateMessage: (messageId: string, content: string, sessionId?: string) => {
        const targetSessionId = sessionId || get().currentSessionId;
        
        if (!targetSessionId) {
          console.error('No session ID provided or selected');
          return;
        }
        
        set(state => {
          const session = state.sessions[targetSessionId];
          if (!session) return state;
          
          const updatedMessages = session.messages.map(msg => 
            msg.id === messageId ? { ...msg, content } : msg
          );
          
          const updatedSession = {
            ...session,
            messages: updatedMessages,
            updatedAt: new Date().toISOString()
          };
          
          return {
            sessions: {
              ...state.sessions,
              [targetSessionId]: updatedSession
            }
          };
        });
      },
      
      deleteMessage: (messageId: string, sessionId?: string) => {
        const targetSessionId = sessionId || get().currentSessionId;
        
        if (!targetSessionId) {
          console.error('No session ID provided or selected');
          return;
        }
        
        set(state => {
          const session = state.sessions[targetSessionId];
          if (!session) return state;
          
          const updatedMessages = session.messages.filter(msg => msg.id !== messageId);
          
          const updatedSession = {
            ...session,
            messages: updatedMessages,
            updatedAt: new Date().toISOString()
          };
          
          return {
            sessions: {
              ...state.sessions,
              [targetSessionId]: updatedSession
            }
          };
        });
      },
      
      clearMessages: (sessionId?: string) => {
        const targetSessionId = sessionId || get().currentSessionId;
        
        if (!targetSessionId) {
          console.error('No session ID provided or selected');
          return;
        }
        
        set(state => {
          const session = state.sessions[targetSessionId];
          if (!session) return state;
          
          const updatedSession = {
            ...session,
            messages: [],
            updatedAt: new Date().toISOString()
          };
          
          return {
            sessions: {
              ...state.sessions,
              [targetSessionId]: updatedSession
            }
          };
        });
      },
      
      // State management
      setLoading: (isLoading: boolean) => set({ isLoading }),
      setError: (error: string | null) => set({ error }),
      
      // Session retrieval
      getCurrentSession: () => {
        const { currentSessionId, sessions } = get();
        return currentSessionId ? sessions[currentSessionId] || null : null;
      },
      
      getMessages: () => {
        const currentSession = get().getCurrentSession();
        return currentSession ? currentSession.messages : [];
      },
    }),
    {
      name: 'chat-store',
      // Only use localStorage on the client side
      storage: isClient 
        ? createJSONStorage(() => localStorage) 
        : createJSONStorage(() => ({
            getItem: () => '{}',
            setItem: () => {},
            removeItem: () => {},
          })),
      skipHydration: true, // Skip hydration to prevent SSR issues
    }
  )
);

export default useChatStore; 