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
     <div className=" bg-angel-gray-50 border-t border-angel-gray-200">
      <form onSubmit={handleSubmit} className="flex flex-col space-y-3">
        <div className="flex items-center space-x-3">
          <button
            type="button"
            className={`flex-shrink-0 p-2.5 rounded-full shadow-md transition-colors duration-200
              ${includeWeb 
                ? 'bg-angel-green-500 text-white hover:bg-angel-green-600' 
                : 'bg-angel-gray-200 text-angel-gray-600 hover:bg-angel-gray-300'
            }`}
            onClick={() => setIncludeWeb(!includeWeb)}
            title={includeWeb ? 'Web content included' : 'Web content excluded'}
          >
            <Globe size={20} />
          </button>
          
          <div className="flex-grow relative">
            <textarea
              className="w-full p-3 pr-12 border border-angel-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-500 resize-none custom-scrollbar-thin"
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
              style={{ maxHeight: '150px' }}
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!message.trim() || isLoading}
              className={`absolute right-3 bottom-3 p-2 rounded-full transition-colors duration-200
                ${!message.trim() || isLoading
                  ? 'bg-violet-200 text-violet-400 cursor-not-allowed'
                  : 'bg-violet-600 text-white hover:bg-violet-700'
                }
              `}
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
          <div className="text-xs text-angel-gray-500 flex items-center justify-center">
            <Globe size={14} className="mr-1 text-angel-green-600" />
            Including Angel One web content in search results
          </div>
        )}
      </form>
    </div>
  );
}; 