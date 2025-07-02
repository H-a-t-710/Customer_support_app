'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

// Use dynamic import with ssr: false to prevent hydration errors
const ChatContainer = dynamic(
  () => import('../components/chat/ChatContainer'),
  { ssr: false }
);

export default function Home() {
  const [isClient, setIsClient] = useState(false);
  
  useEffect(() => {
    setIsClient(true);
  }, []);

  return (
    <div className="h-full w-full flex items-center justify-center">
      <div className="w-full max-w-6xl h-full bg-white rounded-xl shadow-2xl overflow-hidden flex flex-col">
        <div className="flex-grow h-0 relative overflow-hidden">
          {isClient ? <ChatContainer /> : <div className="absolute inset-0 flex items-center justify-center bg-white"><div className="text-violet-500 font-medium text-lg">Loading chat interface...</div></div>}
        </div>
      </div>
    </div>
  );
} 