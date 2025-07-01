'use client';

import React, { ReactNode } from 'react';
import { useStoreHydration } from '@/hooks/useStoreHydration';

interface HydrationProviderProps {
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * Provider component that ensures Zustand stores are hydrated before rendering children
 */
export default function HydrationProvider({
  children,
  fallback = <div className="p-4">Loading application...</div>,
}: HydrationProviderProps) {
  const isHydrated = useStoreHydration();
  
  if (!isHydrated) {
    return <>{fallback}</>;
  }
  
  return <>{children}</>;
} 