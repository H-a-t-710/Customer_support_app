'use client';

import React, { useState } from 'react';
import { Send, Loader2, Globe } from 'lucide-react';

interface MessageInputProps {
  onSendMessage: (message: string, includeWeb: boolean) => void;
  isLoading: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  isLoading,
}) => {
  const [message, setMessage] = useState('');
  const [includeWeb, setIncludeWeb] = useState(true);
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (message.trim() && !isLoading) {
      onSendMessage(message, includeWeb);
      setMessage('');
    }
  };

  return (
    <div className="border-t border-gray-200 p-4 bg-white">
      <form onSubmit={handleSubmit} className="flex flex-col space-y-2">
        <div className="flex items-center">
          <button
            type="button"
            className={`p-2 rounded-md mr-2 flex items-center ${
              includeWeb 
                ? 'bg-green-100 text-green-700' 
                : 'bg-gray-100 text-gray-500'
            }`}
            onClick={() => setIncludeWeb(!includeWeb)}
            title={includeWeb ? 'Web content included' : 'Web content excluded'}
          >
            <Globe size={18} />
          </button>
          
          <div className="flex-1 relative">
            <textarea
              className="w-full p-3 pr-12 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              placeholder="Ask a question about your insurance or Angel One services..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              rows={1}
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!message.trim() || isLoading}
              className={`absolute right-2 top-2.5 p-1.5 rounded-md ${
                !message.trim() || isLoading
                  ? 'text-gray-400'
                  : 'text-blue-600 hover:text-blue-800'
              }`}
            >
              {isLoading ? (
                <Loader2 size={20} className="animate-spin" />
              ) : (
                <Send size={20} />
              )}
            </button>
          </div>
        </div>
        
        {includeWeb && (
          <div className="text-xs text-gray-500 ml-12">
            Including Angel One web content in search results
          </div>
        )}
      </form>
    </div>
  );
}; 