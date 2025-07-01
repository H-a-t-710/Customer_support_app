import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

// Check if code is running on client side
const isClient = typeof window !== 'undefined';

interface AppState {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  notificationCount: number;
}

interface AppActions {
  setTheme: (theme: 'light' | 'dark') => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  incrementNotificationCount: () => void;
  resetNotificationCount: () => void;
}

const useAppStore = create<AppState & AppActions>()(
  persist(
    (set) => ({
      theme: 'light',
      sidebarOpen: true,
      notificationCount: 0,
      
      setTheme: (theme) => set({ theme }),
      
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      
      incrementNotificationCount: () => set((state) => ({ 
        notificationCount: state.notificationCount + 1 
      })),
      
      resetNotificationCount: () => set({ notificationCount: 0 }),
    }),
    {
      name: 'app-storage',
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

export default useAppStore; 