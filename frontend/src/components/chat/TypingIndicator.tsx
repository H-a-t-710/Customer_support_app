'use client';

import React from 'react';

export const TypingIndicator: React.FC = () => {
  return (
    <div className="flex space-x-1 items-center">
      <span className="text-sm text-gray-500">AI is thinking</span>
      <div className="flex space-x-1">
        <div className="animate-bounce w-2 h-2 bg-gray-500 rounded-full" style={{ animationDelay: '0ms' }} />
        <div className="animate-bounce w-2 h-2 bg-gray-500 rounded-full" style={{ animationDelay: '150ms' }} />
        <div className="animate-bounce w-2 h-2 bg-gray-500 rounded-full" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  );
}; 