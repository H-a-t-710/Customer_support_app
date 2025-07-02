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
    <div className="h-full w-full">
      <div className="w-full h-full bg-white rounded-none shadow-none overflow-hidden flex flex-col lg:flex-row">
        {/* Left Section for Chat Introduction */}
        <div className="lg:w-1/3 p-8 bg-gradient-to-br from-violet-600 to-blue-600 text-white flex flex-col justify-between">
          <div>
            <h2 className="text-3xl font-bold mb-4">Insurance Information Assistant</h2>
            <p className="text-violet-100 mb-6">
              Ask me questions about insurance plans, coverage details, and benefits.
            </p>
            <div className="flex items-center text-violet-200">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-file-text mr-2"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>
              <span className="text-lg">Document-based Q&A</span>
            </div>
          </div>
          <div className="mt-8">
            <p className="text-sm text-violet-200 italic">Your go-to source for quick and accurate insurance information.</p>
          </div>
        </div>

        {/* Right Section for Chat Container */}
        <div className="lg:w-2/3 flex flex-col h-full">
          <div className="p-2 bg-angel-gray-50 border-b border-angel-gray-200 flex items-center">
            <h3 className="ml-2 text-xl font-semibold text-angel-gray-800">Insurance & Angel One Support Assistant</h3>
          </div>
          <div className="flex-grow h-full relative">
            {isClient ? <ChatContainer /> : <div className="absolute inset-0 flex items-center justify-center bg-white"><div className="text-violet-500 font-medium text-lg">Loading chat interface...</div></div>}
          </div>
        </div>
      </div>
    </div>
  );
} 