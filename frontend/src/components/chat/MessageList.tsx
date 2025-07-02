'use client';

import React, { useState, useEffect } from 'react';
import { Message, MessageRole, Source } from '@/types/chat';
import { TypingIndicator } from './TypingIndicator';
import { FileText, ChevronDown, ChevronUp, Globe } from 'lucide-react';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  // Create ref for message list to scroll to bottom
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change or loading state changes
  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 p-6 pb-1 space-y-6 bg-angel-white-50 custom-scrollbar">
      {messages.length === 0 && !isLoading && (
        <div className="flex flex-col items-center justify-center h-full text-center text-angel-gray-500 p-8">
          <FileText size={56} className="mb-6 text-violet-500" />
          <h3 className="text-2xl font-semibold mb-3 text-angel-gray-700">Start a Conversation</h3>
          <p className="text-md text-angel-gray-600 max-w-sm">
            Ask questions about insurance plans, coverage details, or Angel One & apos;s investment services.
          </p>
        </div>
      )}
      
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}
      
      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-angel-gray-100 rounded-2xl p-3 max-w-[80%] border border-angel-gray-200 shadow-sm">
            <TypingIndicator />
          </div>
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
};

const MessageItem: React.FC<{ message: Message }> = ({ message }) => {
  const isUser = message.role === MessageRole.USER;
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div 
        className={`rounded-2xl p-4 shadow-md max-w-[75%] ${
          isUser 
            ? 'bg-violet-600 text-white rounded-br-none' 
            : 'bg-angel-gray-100 text-angel-gray-800 rounded-bl-none border border-angel-gray-200'
        }`}
      >
        <div className="whitespace-pre-wrap prose prose-p:leading-normal prose-li:leading-normal prose-a:text-violet-200 prose-blockquote:text-angel-gray-200 break-words text-sm sm:text-base max-w-none">
          {/* Format message content with proper markdown */}
          {formatMessageContent(message.content)}
        </div>
        
        {message.sources && message.sources.length > 0 && (
          <SourceList sources={message.sources} />
        )}
      </div>
    </div>
  );
};

const formatMessageContent = (content: string): React.ReactNode => {
  // Replace both document and web document citations with styled spans
  const formattedContent = content
    .split(/(\[Document \d+\]|\[Web Document \d+\])/g)
    .map((part, index) => {
      if (part.match(/\[Document \d+\]/)) {
        return (
          <span key={index} className="font-medium text-violet-200 bg-violet-700 px-1.5 py-0.5 rounded-md whitespace-nowrap text-xs">
            {part}
          </span>
        );
      }
      if (part.match(/\[Web Document \d+\]/)) {
        return (
          <span key={index} className="font-medium text-angel-green-200 bg-angel-green-700 px-1.5 py-0.5 rounded-md whitespace-nowrap text-xs">
            {part}
          </span>
        );
      }
      return <span key={index}>{part}</span>;
    });
  
  return formattedContent;
};

const SourceList: React.FC<{ sources: Source[] }> = ({ sources }) => {
  // Use useState with a default value
  const [expanded, setExpanded] = useState(false);
  // Use useEffect to ensure client-side only rendering for interactive elements
  const [isClient, setIsClient] = useState(false);
  
  useEffect(() => {
    setIsClient(true);
  }, []);

  if (sources.length === 0) return null;

  return (
    <div className="mt-4 pt-3 border-t border-angel-gray-300 text-xs text-angel-gray-600">
      {isClient && (
        <button 
          className="flex items-center text-violet-700 hover:text-violet-900 font-medium mb-2 transition-colors duration-200"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? (
            <>
              <ChevronUp size={16} className="mr-1" />
              Hide sources ({sources.length})
            </>
          ) : (
            <>
              <ChevronDown size={16} className="mr-1" />
              Show sources ({sources.length})
            </>
          )}
        </button>
      )}
      
      {isClient && expanded && (
        <div className="space-y-2 mt-2 max-h-48 overflow-y-auto pr-2 custom-scrollbar-thumb-angel-gray-300">
          {sources.map((source, idx) => (
            <SourceItem key={idx} source={source} index={idx} />
          ))}
        </div>
      )}
    </div>
  );
};

const SourceItem: React.FC<{ source: Source, index: number }> = ({ source, index }) => {
  const [showContent, setShowContent] = useState(false);
  const [isClient, setIsClient] = useState(false);
  
  useEffect(() => {
    setIsClient(true);
  }, []);
  
  // Get page info for display
  const pageInfo = source.metadata.page 
    ? `Page ${source.metadata.page}`
    : '';
  
  // Determine if source is web or document based on the URL in metadata.source
  let isWebSource = false;
  let displaySource = source.metadata.source;
  let sourceUrl: string | undefined = undefined;

  try {
    const urlObj = new URL(source.metadata.source);
    isWebSource = true;
    displaySource = urlObj.hostname; // Display hostname for web sources
    sourceUrl = source.metadata.source; // Store full URL for the link
      } catch {
    // Not a valid URL, treat as document or other
      // Remove file extensions
    const withoutExtension = source.metadata.source.replace(/\.(pdf|docx|doc|txt)$/i, '');
      // Replace underscores with spaces
      const withSpaces = withoutExtension.replace(/_/g, ' ');
      // Capitalize words
    displaySource = withSpaces
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    isWebSource = false;
    }

  // Calculate similarity percentage for display
  const similarityPercent = source.similarity 
    ? Math.round(source.similarity * 100) 
    : null;

  return (
    <div className="border border-angel-gray-200 rounded-lg overflow-hidden bg-white shadow-sm">
      {isClient && (
        <>
          <div 
            className="flex justify-between items-center p-3 bg-angel-gray-100 cursor-pointer hover:bg-angel-gray-200 transition-colors duration-200"
            onClick={() => setShowContent(!showContent)}
          >
            <div className="font-medium flex items-center text-angel-gray-700">
              {isWebSource ? (
                <Globe size={18} className="mr-2 text-angel-green-600" />
              ) : (
                <FileText size={18} className="mr-2 text-violet-600" />
              )}
              <span>
                {displaySource}
                {pageInfo && <span className="ml-2 text-angel-gray-500">({pageInfo})</span>}
                </span>
            </div>
            <div className="flex items-center">
              {similarityPercent !== null && (
                <span className="text-xs bg-violet-100 text-violet-700 px-2 py-0.5 rounded-full mr-2">
                  {similarityPercent}%
                </span>
              )}
              {showContent ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </div>
          </div>
          
          {showContent && (
            <div className="p-3 text-angel-gray-700 prose prose-sm max-w-none leading-snug">
              <p className="line-clamp-3 text-sm">
              {source.content}
              </p>
              {sourceUrl && (
                  <a 
                  href={sourceUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                  className="text-violet-500 hover:text-violet-700 text-xs mt-2 inline-block"
                  >
                  Read more
                  </a>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}; 