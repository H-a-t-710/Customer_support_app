'use client';

import React from 'react';

export const TypingIndicator: React.FC = () => {
  return (
    <div className="flex items-center space-x-2 text-angel-gray-500 text-sm">
      <span>AI is thinking</span>
      <div className="flex items-center space-x-1">
        <div className="w-2 h-2 bg-violet-500 rounded-full animate-pulse" style={{ animationDelay: '0s' }} />
        <div className="w-2 h-2 bg-violet-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
        <div className="w-2 h-2 bg-violet-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
      </div>
    </div>
  );
}; 