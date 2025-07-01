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
    <div className="flex-1 overflow-y-auto p-4 space-y-6">
      {messages.length === 0 && !isLoading && (
        <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 p-8">
          <FileText size={48} className="mb-4 text-blue-500" />
          <h3 className="text-xl font-medium mb-2">Insurance & Angel One Support Assistant</h3>
          <p>Ask questions about insurance plans, coverage details, or Angel One's investment services.</p>
        </div>
      )}
      
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}
      
      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-gray-100 rounded-lg p-3 max-w-[80%] border border-gray-200 shadow-sm">
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
        className={`rounded-lg p-4 max-w-[85%] shadow-sm ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : 'bg-white text-gray-800 border border-gray-200'
        }`}
      >
        <div className="whitespace-pre-wrap prose prose-sm max-w-none">
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
          <span key={index} className="font-medium text-blue-700 bg-blue-50 px-1 rounded">
            {part}
          </span>
        );
      }
      if (part.match(/\[Web Document \d+\]/)) {
        return (
          <span key={index} className="font-medium text-green-700 bg-green-50 px-1 rounded">
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
    <div className="mt-4 text-sm border-t border-gray-200 pt-3">
      {isClient && (
        <button 
          className="flex items-center text-blue-600 hover:text-blue-800 font-medium mb-2"
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
        <div className="space-y-3 mt-2">
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
  
  // Determine if source is web or document
  const isWebSource = source.metadata.source_type === 'web' || source.metadata.source_type === 'web_faq';
  
  // Format source name based on type
  const formatSourceName = (name: string, isWeb: boolean) => {
    if (isWeb) {
      // For web sources, extract domain or use full URL
      try {
        const url = new URL(name);
        return url.hostname || name;
      } catch {
        return name; // Return as is if not a valid URL
      }
    } else {
      // Format document name as before
      // Remove file extensions
      const withoutExtension = name.replace(/\.(pdf|docx|doc|txt)$/i, '');
      // Replace underscores with spaces
      const withSpaces = withoutExtension.replace(/_/g, ' ');
      // Capitalize words
      return withSpaces
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    }
  };

  // Calculate similarity percentage for display
  const similarityPercent = source.similarity 
    ? Math.round(source.similarity * 100) 
    : null;

  return (
    <div className="border border-gray-200 rounded-md overflow-hidden bg-gray-50">
      {isClient && (
        <>
          <div 
            className="flex justify-between items-center p-3 bg-gray-100 cursor-pointer hover:bg-gray-200"
            onClick={() => setShowContent(!showContent)}
          >
            <div className="font-medium flex items-center">
              {isWebSource ? (
                <Globe size={16} className="mr-2 text-green-600" />
              ) : (
                <FileText size={16} className="mr-2 text-blue-600" />
              )}
              <span>{formatSourceName(source.metadata.source, isWebSource)}</span>
              {pageInfo && <span className="ml-2 text-gray-600 text-xs bg-gray-200 px-2 py-0.5 rounded-full">{pageInfo}</span>}
              {source.metadata.source_type && (
                <span 
                  className={`ml-2 text-xs px-2 py-0.5 rounded-full ${
                    isWebSource 
                      ? 'bg-green-50 text-green-600' 
                      : 'bg-blue-50 text-blue-600'
                  }`}
                >
                  {source.metadata.source_type}
                </span>
              )}
              {similarityPercent && (
                <span className="ml-2 text-gray-600 text-xs bg-gray-200 px-2 py-0.5 rounded-full">
                  {similarityPercent}% match
                </span>
              )}
            </div>
            <button className="text-xs flex items-center text-gray-600">
              {showContent ? (
                <>
                  <ChevronUp size={14} className="mr-1" />
                  Hide
                </>
              ) : (
                <>
                  <ChevronDown size={14} className="mr-1" />
                  Show
                </>
              )}
            </button>
          </div>
          
          {showContent && (
            <div className="p-3 bg-white text-sm whitespace-pre-wrap max-h-60 overflow-y-auto border-t border-gray-200">
              {source.content}
              {isWebSource && source.metadata.source.startsWith('http') && (
                <div className="mt-2 pt-2 border-t border-gray-100">
                  <a 
                    href={source.metadata.source} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-green-600 hover:text-green-800 text-xs flex items-center"
                  >
                    <Globe size={12} className="mr-1" />
                    View Source
                  </a>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}; 