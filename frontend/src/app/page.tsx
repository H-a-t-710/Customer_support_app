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
    <div className="max-w-5xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="p-4 bg-blue-50 border-b border-blue-100">
          <h2 className="text-xl font-semibold text-blue-800">Insurance Information Assistant</h2>
          <p className="text-sm text-gray-600">
            Ask me questions about insurance plans, coverage details, and benefits.
          </p>
        </div>
        {isClient ? <ChatContainer /> : <div className="p-4">Loading chat interface...</div>}
      </div>
      
      <div className="mt-8 bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-3">About This Chatbot</h3>
        <p className="mb-2">
          This chatbot uses Retrieval-Augmented Generation (RAG) to provide accurate answers about insurance plans based on the provided documents.
        </p>
        <p className="mb-2">
          The chatbot can answer questions about plan benefits, coverage details, deductibles, and more.
        </p>
        <p className="text-sm text-gray-500">
          Note: This chatbot will only answer questions based on information in the provided documentation. For questions outside this scope, it will respond with "I don't know".
        </p>
      </div>
    </div>
  );
} 