import { useState, useEffect } from 'react';
import useChatStore from '@/store/chatStore';
import useAppStore from '@/store/appStore';

/**
 * Hook to handle store hydration to prevent hydration mismatches
 */
export function useStoreHydration() {
  const [isHydrated, setIsHydrated] = useState(false);
  
  // Wait for next tick after mount to hydrate stores
  useEffect(() => {
    // Get the stores
    const chatStore = useChatStore.persist;
    const appStore = useAppStore.persist;
    
    // Create a promise that resolves when both stores are hydrated
    const hydratePromise = Promise.all([
      chatStore.rehydrate(),
      appStore.rehydrate()
    ]);
    
    // When both stores are hydrated, set isHydrated to true
    hydratePromise.then(() => {
      setIsHydrated(true);
    });
    
    // Return a cleanup function
    return () => {
      // Optional: Handle cleanup if needed
    };
  }, []);
  
  return isHydrated;
} 