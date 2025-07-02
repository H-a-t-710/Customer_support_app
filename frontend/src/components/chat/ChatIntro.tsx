import React from 'react';

const ChatIntro: React.FC = () => (
  <div className="h-full p-8 bg-gradient-to-br from-violet-600 to-blue-600 text-white flex flex-col justify-between">
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
);

export default ChatIntro; 